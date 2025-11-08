# OMIM Gene-to-Disease Ingest

## Overview

This ingest transforms OMIM morbidmap data into Biolink-compliant gene-to-disease associations.

**Source:** OMIM morbidmap.txt
**URL:** https://rmalenf1.ext.unb.ca/BIOL3933/morbidmap.txt
**Rows processed:** 7,413 data rows (7,437 total including headers)
**Associations created:** 5,990 gene-to-disease associations

## Output

**Total:** 5,990 associations (edges only, no nodes)

**By Association Type:**
- **CausalGeneToDiseaseAssociation:** 5,255 (87.7%)
- **CorrelatedGeneToDiseaseAssociation:** 735 (12.3%)

**By Predicate:**
- **biolink:causes:** 5,255 (confidence level 3)
- **biolink:contributes_to:** ~600 (confidence levels 1 and 2)
- **biolink:predisposes_to_condition:** ~135 (susceptibility cases)

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
**Confidence (3)** → Causal (molecular basis = causation)
**Confidence (1,2)** → Correlated (mapping = correlation)
**Confidence (4)** → Skip (not gene-to-disease)

### Predicate Selection
**Susceptibility markers** → `biolink:predisposes_to_condition` (overrides confidence)
**Confidence (3)** → `biolink:causes`
**Confidence (1,2)** → `biolink:contributes_to`

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
