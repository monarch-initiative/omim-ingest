# OMIM Gene-to-Disease Ingest

## Overview

This ingest transforms OMIM morbidmap data into Biolink-compliant gene-to-disease associations.

**Source:** OMIM morbidmap.txt
**URL:** https://rmalenf1.ext.unb.ca/BIOL3933/morbidmap.txt
**Rows processed:** 7,413 data rows (7,437 total including headers)
**Associations created:** {{ get_total_edges() }} gene-to-disease associations

## Output

**Total:** {{ get_total_edges() }} associations (edges only, no nodes)

**By Association Type:**
- **CausalGeneToDiseaseAssociation:** {{ get_stat('CausalGeneToDiseaseAssociation_count') }} ({{ get_stat('CausalGeneToDiseaseAssociation_pct') }}%)
- **CorrelatedGeneToDiseaseAssociation:** {{ get_stat('CorrelatedGeneToDiseaseAssociation_count') }} ({{ get_stat('CorrelatedGeneToDiseaseAssociation_pct') }}%)

**By Predicate:**
- **biolink:causes:** {{ get_stat('causes_count') }} ({{ get_stat('causes_pct') }}% - confidence level 3)
- **biolink:contributes_to:** {{ get_stat('contributes_to_count') }} ({{ get_stat('contributes_to_pct') }}% - confidence levels 1 and 2)
- **biolink:predisposes_to_condition:** {{ get_stat('predisposes_to_condition_count') }} ({{ get_stat('predisposes_to_condition_pct') }}% - susceptibility cases)

## Biolink Mappings

### Association Categories

#### CausalGeneToDiseaseAssociation
- **Trigger:** OMIM confidence level (3) = molecular basis known
- **Predicate:** `biolink:causes` (RO:0003303)
- **Subject:** Gene (OMIM MIM Number)
- **Object:** Disease/Phenotype (OMIM ID)

#### CorrelatedGeneToDiseaseAssociation
- **Triggers:**
  - Confidence (1) = gene mapped
  - Confidence (2) = phenotype mapped
  - Susceptibility markers `{}`
- **Predicates:**
  - `biolink:contributes_to` (RO:0002326) for levels 1/2
  - `biolink:predisposes_to_condition` for susceptibility
- **Subject:** Gene (OMIM MIM Number)
- **Object:** Disease/Phenotype (OMIM ID)

### Field Mappings

| Input Column | Output Field | Processing |
|--------------|--------------|------------|
| MIM Number | subject | Prefix with `OMIM:` |
| Phenotype | object | Extract OMIM ID, prefix with `OMIM:` |
| Phenotype | predicate | Based on confidence level and markers |
| Phenotype | category | Association type from confidence level |

## OMIM Format

### Phenotype Column Structure
```
[?]{Disease Name}, OMIM_ID (CONFIDENCE)
```

**Special Markers:**
- `?` = provisional relationship
- `[]` = nondiseases (genetic variations)
- `{}` = susceptibility to multifactorial disorders

**Confidence Levels:**
- `(1)` = gene mapped
- `(2)` = phenotype mapped
- `(3)` = molecular basis known
- `(4)` = chromosomal abnormality (SKIPPED)

### Examples

```tsv
# Causal (3)
17,20-lyase deficiency, isolated, 202110 (3)	CYP17A1	609300	10q24.32

# Provisional (1)
?ACAT2 deficiency, 614055 (1)	ACAT2	100678	6q25.3

# Susceptibility
{46XY sex reversal 8}, 614279 (3)	AKR1C4	600451	10p15.1
```

## Decisions

### Association Type Selection
- **Confidence (3)** → CausalGeneToDiseaseAssociation (molecular basis = causation)
- **Confidence (1,2)** → CorrelatedGeneToDiseaseAssociation (mapping = correlation)
- **Susceptibility {}** → CorrelatedGeneToDiseaseAssociation (predisposition, not direct causation)
- **Confidence (4)** → Skip (chromosomal abnormalities, not gene-to-disease)

### Predicate Selection

| OMIM Marker | Predicate | RO Term | Rationale |
|-------------|-----------|---------|-----------|
| `{}` (any confidence) | `biolink:predisposes_to_condition` | RO:0019501* | Susceptibility markers indicate predisposition |
| Confidence (3), no `{}` | `biolink:causes` | RO:0003303 | Molecular basis known = causation |
| Confidence (1,2), no `{}` | `biolink:contributes_to` | RO:0002326 | Mapping known, mechanism unclear |

*RO:0019501 "confers susceptibility to condition" - not yet in Biolink model but semantically aligned

**Priority Rule:** Susceptibility markers `{}` override confidence levels. Even if molecular basis is known (confidence 3), the presence of `{}` indicates a susceptibility relationship, not direct causation.

**Why predisposes_to_condition for susceptibility?**

OMIM uses `{}` to mark "susceptibility to multifactorial disorders." The Relation Ontology (RO) explicitly defines susceptibility (RO:0019501) as **distinct from** general contribution (RO:0002326), justifying use of the more specific `biolink:predisposes_to_condition` predicate rather than generic `biolink:contributes_to`.

See detailed justification: [predicate_justification.md](predicate_justification.md)

### Comparison with HPOA ETL

Previous HPOA ETL processing of OMIM data used `biolink:contributes_to` for POLYGENIC/susceptibility associations. Our analysis shows 68.7% agreement overall, with disagreements primarily due to our more semantically precise handling of susceptibility (using `predisposes_to_condition`).

See: [comparison_with_hpoa.md](comparison_with_hpoa.md)

### Exclusions
- Chromosomal abnormalities (4): ~24 rows
- Missing OMIM IDs: ~1,375 rows
- Total excluded: ~1,399 rows

## Testing

7 test cases covering:
- Standard causal (3)
- Provisional correlated (1)
- Nondiseases with brackets
- Susceptibility with braces
- Combined provisional + susceptibility
- Missing OMIM ID (excluded)
- Chromosomal abnormality (excluded)

**Status:** All tests pass ✓
