"""
Test file for OMIM gene-to-disease transform.

Tests are based on actual OMIM morbidmap.txt data to handle various edge cases.

OMIM morbidmap format documentation:
- Numbers in parentheses indicate confidence levels:
  (1) = disorder positioned by mapping of wildtype gene → CorrelatedGeneToDiseaseAssociation
  (2) = disease phenotype itself was mapped → CorrelatedGeneToDiseaseAssociation
  (3) = molecular basis of disorder is known → CausalGeneToDiseaseAssociation
  (4) = chromosomal abnormality → SKIP (not gene-to-disease)
- Brackets [ ] = "nondiseases" (genetic variations with abnormal lab values)
- Braces { } = mutations contributing to susceptibility to multifactorial disorders
- Question mark ? = provisional relationship between phenotype and gene

Biolink Model Mappings (from biolink_model SchemaView research):
- CausalGeneToDiseaseAssociation uses predicate subproperty of "affects"
  → Use "biolink:causes" (RO:0003303) for confidence level (3)
- CorrelatedGeneToDiseaseAssociation uses predicate subproperty of "correlated with"
  → Use "biolink:contributes_to" (RO:0002326) for levels (1) and (2)
  → Use "biolink:predisposes_to_condition" for susceptibility cases {braces}

See the Koza documentation for more information on testing transforms:
https://koza.monarchinitiative.org/Usage/testing/
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from biolink_model.datamodel.pydanticmodel_v2 import (
    CausalGeneToDiseaseAssociation,
    CorrelatedGeneToDiseaseAssociation
)
from omim_ingest.transform import transform_record


# Test data fixtures based on actual OMIM morbidmap.txt rows


@pytest.fixture
def standard_row_entities():
    """Standard row with confidence level (3)."""
    row = {
        "Phenotype": "17,20-lyase deficiency, isolated, 202110 (3)",
        "Gene Symbols": "CYP17A1, CYP17, P450C17",
        "MIM Number": "609300",
        "Cyto Location": "10q24.32"
    }
    # Pass None for koza_transform since we don't use maps/lookups
    return transform_record(None, row)


@pytest.fixture
def provisional_row_entities():
    """Row with question mark indicating provisional relationship."""
    row = {
        "Phenotype": "?ACAT2 deficiency, 614055 (1)",
        "Gene Symbols": "ACAT2",
        "MIM Number": "100678",
        "Cyto Location": "6q25.3"
    }
    return transform_record(None, row)


@pytest.fixture
def nondisease_row_entities():
    """Row with square brackets indicating 'nondisease'."""
    row = {
        "Phenotype": "[?Birbeck granule deficiency], 613393 (3)",
        "Gene Symbols": "CD207, LANGERIN, CLEC4K",
        "MIM Number": "604862",
        "Cyto Location": "2p13.3"
    }
    return transform_record(None, row)


@pytest.fixture
def susceptibility_row_entities():
    """Row with curly braces indicating susceptibility to multifactorial disorder."""
    row = {
        "Phenotype": "{46XY sex reversal 8, modifier of}, 614279 (3)",
        "Gene Symbols": "AKR1C4, CHDR, CDR, HAKRA, DD4",
        "MIM Number": "600451",
        "Cyto Location": "10p15.1"
    }
    return transform_record(None, row)


@pytest.fixture
def provisional_susceptibility_row_entities():
    """Row with both question mark and curly braces."""
    row = {
        "Phenotype": "?{Amyotrophic lateral sclerosis, susceptibility to}, 105400 (3)",
        "Gene Symbols": "NEFH, CMT2CC",
        "MIM Number": "162230",
        "Cyto Location": "22q12.2"
    }
    return transform_record(None, row)


@pytest.fixture
def confidence_level_2_row_entities():
    """Row with confidence level (2)."""
    row = {
        "Phenotype": "?Anal canal carcinoma (2)",
        "Gene Symbols": "ANC",
        "MIM Number": "105580",
        "Cyto Location": "11q22-qter"
    }
    return transform_record(None, row)


@pytest.fixture
def chromosomal_abnormality_row_entities():
    """Row with confidence level (4) indicating chromosomal abnormality."""
    row = {
        "Phenotype": "3p- syndrome (4)",
        "Gene Symbols": "DEL3pterp25, C3DELpterp25",
        "MIM Number": "613792",
        "Cyto Location": "3pter-p25"
    }
    return transform_record(None, row)


# Test functions


def test_standard_association(standard_row_entities):
    """Test parsing of standard gene-disease association with confidence (3)."""
    assert standard_row_entities
    assert len(standard_row_entities) == 1

    association = standard_row_entities[0]
    assert isinstance(association, CausalGeneToDiseaseAssociation)
    assert association.subject == "OMIM:609300"  # Gene MIM number
    assert association.object == "OMIM:202110"  # Disease OMIM ID
    assert association.predicate == "biolink:causes"  # Molecular basis known


def test_provisional_association(provisional_row_entities):
    """Test parsing of provisional relationship (starts with ?) with confidence (1)."""
    assert provisional_row_entities
    assert len(provisional_row_entities) == 1

    association = provisional_row_entities[0]
    assert isinstance(association, CorrelatedGeneToDiseaseAssociation)
    assert association.subject == "OMIM:100678"
    assert association.object == "OMIM:614055"
    assert association.predicate == "biolink:contributes_to"  # Confidence level 1


def test_nondisease_association(nondisease_row_entities):
    """Test parsing of nondisease (genetic variation with abnormal lab values)."""
    assert nondisease_row_entities
    assert len(nondisease_row_entities) == 1

    association = nondisease_row_entities[0]
    assert isinstance(association, CausalGeneToDiseaseAssociation)
    assert association.subject == "OMIM:604862"
    assert association.object == "OMIM:613393"
    assert association.predicate == "biolink:causes"  # Confidence level 3


def test_susceptibility_association(susceptibility_row_entities):
    """Test parsing of susceptibility to multifactorial disorder (with braces)."""
    assert susceptibility_row_entities
    assert len(susceptibility_row_entities) == 1

    association = susceptibility_row_entities[0]
    assert isinstance(association, CorrelatedGeneToDiseaseAssociation)
    assert association.subject == "OMIM:600451"
    assert association.object == "OMIM:614279"
    assert association.predicate == "biolink:predisposes_to_condition"  # Susceptibility


def test_provisional_susceptibility_association(provisional_susceptibility_row_entities):
    """Test parsing of provisional susceptibility (both ? and {})."""
    assert provisional_susceptibility_row_entities
    assert len(provisional_susceptibility_row_entities) == 1

    association = provisional_susceptibility_row_entities[0]
    assert isinstance(association, CorrelatedGeneToDiseaseAssociation)
    assert association.subject == "OMIM:162230"
    assert association.object == "OMIM:105400"
    assert association.predicate == "biolink:predisposes_to_condition"  # Susceptibility takes precedence


def test_confidence_level_2(confidence_level_2_row_entities):
    """Test that confidence level (2) is captured correctly."""
    # This row has no phenotype OMIM ID, should return empty list
    assert confidence_level_2_row_entities == []


def test_chromosomal_abnormality(chromosomal_abnormality_row_entities):
    """Test that chromosomal abnormalities (4) are skipped (not gene-to-disease)."""
    # Chromosomal abnormalities have same ID for gene and disease, skip them
    assert chromosomal_abnormality_row_entities == []
