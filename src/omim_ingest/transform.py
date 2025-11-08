"""
Transform for omim-ingest.

This module transforms OMIM morbidmap data into Biolink model gene-to-disease associations.

OMIM morbidmap format:
- Phenotype column contains: disease name, OMIM ID, and confidence level in parentheses
- Brackets/braces indicate special types: [ ] = nondiseases, { } = susceptibility
- Question mark prefix = provisional relationship
- Confidence levels: (1)=mapped gene, (2)=mapped phenotype, (3)=molecular basis known, (4)=chromosomal

Biolink mapping:
- (3) → CausalGeneToDiseaseAssociation with "biolink:causes"
- (1)/(2) → CorrelatedGeneToDiseaseAssociation with "biolink:contributes_to"
- { } susceptibility → "biolink:predisposes_to_condition"
- (4) chromosomal → skip (not gene-to-disease)
"""

import re
import uuid
from typing import Any

import koza
from koza import KozaTransform
from biolink_model.datamodel.pydanticmodel_v2 import (
    CausalGeneToDiseaseAssociation,
    CorrelatedGeneToDiseaseAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum
)


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list:
    """
    Transform OMIM morbidmap row into Biolink gene-to-disease associations.

    Args:
        koza_transform: Koza transform context (not used, no maps)
        row: Dictionary containing row data with keys:
            - Phenotype: disease name, OMIM ID, confidence level
            - Gene Symbols: gene symbols (comma-separated)
            - MIM Number: gene OMIM ID
            - Cyto Location: chromosomal location

    Returns:
        list: List containing single association, or empty list if skipped
    """
    phenotype = row["Phenotype"]
    gene_mim = row["MIM Number"]

    # Parse phenotype string to extract:
    # - OMIM ID
    # - Confidence level (1-4)
    # - Special markers (?, [ ], { })

    # Extract confidence level from parentheses at end
    confidence_match = re.search(r'\((\d)\)\s*$', phenotype)
    if not confidence_match:
        return []  # No confidence level, skip

    confidence_level = int(confidence_match.group(1))

    # Skip chromosomal abnormalities (4) - not gene-to-disease
    if confidence_level == 4:
        return []

    # Extract OMIM ID for disease/phenotype
    # Pattern: finds 6-digit number followed by space and (confidence)
    omim_id_match = re.search(r'(\d{6})\s+\(\d\)', phenotype)
    if not omim_id_match:
        return []  # No OMIM ID for disease, skip

    disease_omim_id = omim_id_match.group(1)

    # Check for special markers
    is_susceptibility = '{' in phenotype  # Susceptibility to multifactorial disorder
    is_provisional = phenotype.strip().startswith('?')  # Provisional relationship
    is_nondisease = '[' in phenotype  # Nondisease (genetic variation)

    # Determine predicate and association type based on confidence and markers
    if is_susceptibility:
        # Susceptibility uses predisposes_to_condition regardless of confidence
        predicate = "biolink:predisposes_to_condition"
        association_class = CorrelatedGeneToDiseaseAssociation
    elif confidence_level == 3:
        # Molecular basis known - causal relationship
        predicate = "biolink:causes"
        association_class = CausalGeneToDiseaseAssociation
    else:  # confidence_level in (1, 2)
        # Mapped gene or phenotype - correlated relationship
        predicate = "biolink:contributes_to"
        association_class = CorrelatedGeneToDiseaseAssociation

    # Create association
    association = association_class(
        id=f"uuid:{uuid.uuid4()}",
        subject=f"OMIM:{gene_mim}",
        predicate=predicate,
        object=f"OMIM:{disease_omim_id}",
        knowledge_level=KnowledgeLevelEnum.not_provided,
        agent_type=AgentTypeEnum.not_provided,
    )

    return [association]
