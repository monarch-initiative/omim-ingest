# Predicate Selection Rationale

## Overview

This document explains the scientific justification for our predicate choices when transforming OMIM morbidmap.txt data into Biolink-compliant gene-to-disease associations.

## Predicate Assignment Rules

| OMIM Indicator | Relationship Type | Predicate | RO Term | Association Type |
|----------------|-------------------|-----------|---------|------------------|
| Confidence (3) | Causal | `biolink:causes` | RO:0003303 | CausalGeneToDiseaseAssociation |
| Confidence (1,2) | Correlation/Mapping | `biolink:contributes_to` | RO:0002326 | CorrelatedGeneToDiseaseAssociation |
| Markers `{}` | Susceptibility | `biolink:predisposes_to_condition` | RO:0019501* | CorrelatedGeneToDiseaseAssociation |

*RO:0019501 is not yet mapped in Biolink model but is semantically aligned

## Critical Decision: predisposes_to_condition vs contributes_to

The most important decision in this ingest is using `biolink:predisposes_to_condition` for OMIM susceptibility markers `{}` rather than the more generic `biolink:contributes_to`.

### OMIM Susceptibility Markers

OMIM uses curly braces `{}` to indicate:

> "Mutations that contribute to susceptibility to multifactorial disorders (e.g., diabetes, asthma) or to susceptibility to infection"

**Examples from morbidmap.txt:**
```tsv
{?Schizophrenia susceptibility 18}, 615232 (3)	SLC1A1	133550	9p24.2
{?Breast cancer susceptibility}, 114480 (1)	NQO2	160998	6p25.2
{?Autism susceptibility 16}, 613410 (3)	SLC9A9	608396	3q24
{?Obesity, susceptibility to}, 601665 (3)	CARTPT	602606	5q13.2
{?Parkinson disease 5, susceptibility to}, 613643 (3)	UCHL1	191342	4p13
```

Note: All explicitly use the word "**susceptibility**" in the phenotype name.

### Evidence from the Relation Ontology (RO)

The Relation Ontology (RO) defines susceptibility as a **distinct relationship type** separate from general contribution:

#### RO:0019501 - "confers susceptibility to condition"

**Definition:** "Relates a gene to condition, such that a variation in this gene predisposes to the development of a condition."

**Significance:** This precisely describes what OMIM `{}` markers represent - genetic variants that predispose to disease development.

#### RO:0002326 - "contributes to"

**Definition:** "Holds between two entities where the occurrence, existence, or activity of one contributes to the occurrence or generation of the other"

**Usage:** Generic contribution relationships (e.g., enzyme subunits contributing to enzyme activity)

**Limitation:** Not specific to susceptibility or predisposition

### Key Finding

**The Relation Ontology explicitly separates susceptibility (RO:0019501) from general contribution (RO:0002326).**

This is evidence that susceptibility relationships require a more specific predicate than the generic "contributes to."

### Biolink Model Alignment

#### biolink:predisposes_to_condition

- **Description:** "Holds between two entities where the presence or application of one increases the chance that the other will come to be"
- **Parent predicate:** `affects likelihood of`
- **Semantic mapping:** `SEMMEDDB:PREDISPOSES`
- **Match:** Directly describes susceptibility/predisposition

#### biolink:contributes_to

- **Description:** "Holds between two entities where the occurrence, existence, or activity of one contributes to the occurrence or generation of the other"
- **Parent predicate:** `related to at instance level`
- **RO mapping:** `RO:0002326`
- **Narrow mappings:** Includes `MONDO:predisposes_towards`
- **Problem:** The fact that predisposition is a **narrow mapping** indicates predisposition is MORE SPECIFIC than general contribution

### Semantic Precision

Our approach maintains three distinct relationship types:

1. **Causal** (confidence 3, no `{}`): Gene mutation directly causes disease → `biolink:causes`
2. **Correlation/Mapping** (confidence 1 or 2, no `{}`): Gene-disease association established but mechanism unclear → `biolink:contributes_to`
3. **Susceptibility** (any confidence with `{}`): Genetic variant increases risk/predisposition → `biolink:predisposes_to_condition`

Using `biolink:contributes_to` for susceptibility would:
- ❌ Conflate three distinct relationship types into two
- ❌ Lose the semantic distinction OMIM makes with `{}` markers
- ❌ Ignore RO's explicit susceptibility-specific terms
- ❌ Discard OMIM's consistent use of "susceptibility" terminology

### Priority Rules

Susceptibility markers **override** confidence levels:

- `{Disease}, 614279 (3)` → `predisposes_to_condition` (not `causes`)
- `{Disease}, 114480 (1)` → `predisposes_to_condition` (not `contributes_to`)

**Rationale:** OMIM explicitly marks these as susceptibility relationships, which is semantically distinct from causation even when molecular basis is known (confidence 3).

## Comparison with Previous HPOA ETL

The previous HPOA ETL process (via genes_to_disease.txt from MedGen) used `biolink:contributes_to` for POLYGENIC associations, which include susceptibility relationships.

### Key Differences

| Aspect | HPOA Approach | Our Approach |
|--------|---------------|--------------|
| Susceptibility predicate | `biolink:contributes_to` | `biolink:predisposes_to_condition` |
| Semantic precision | Generic contribution | Specific susceptibility |
| RO alignment | RO:0002326 (contributes to) | RO:0019501* (confers susceptibility) |
| Information content | Lower | Higher |

*Not yet in Biolink model but semantically aligned

### Agreement Analysis

Comparing our output with HPOA's OMIM-derived associations:
- **68.7% agreement** on predicates
- **31.3% disagreement** primarily due to susceptibility handling

The disagreement is not an error - it reflects our more semantically precise handling of susceptibility relationships.

## Recommendations

### For This Ingest
✅ **Use `biolink:predisposes_to_condition` for OMIM susceptibility markers** - scientifically justified and semantically accurate

### For Biolink Model
📝 **Add RO:0019501 mapping** to `biolink:predisposes_to_condition`:
```yaml
biolink:predisposes_to_condition:
  exact_mappings:
    - SEMMEDDB:PREDISPOSES
    - RO:0019501  # confers susceptibility to condition (PROPOSED)
```

### For HPOA ETL
🔄 **Consider updating** to use `biolink:predisposes_to_condition` for POLYGENIC/susceptibility associations to improve semantic precision

## References

- [OMIM Morbid Map Documentation](https://www.omim.org/help/faq#1_3)
- [Relation Ontology (RO)](http://www.obofoundry.org/ontology/ro.html)
- [RO:0019501 - confers susceptibility to condition](https://www.ebi.ac.uk/ols4/ontologies/ro)
- [Biolink Model](https://biolink.github.io/biolink-model/)
- Comparison analysis: `comparison_with_hpoa.md`

## Conclusion

Our use of `biolink:predisposes_to_condition` for OMIM susceptibility markers is:

✅ Scientifically justified by RO's explicit susceptibility terms
✅ Semantically aligned with OMIM's terminology and intent
✅ Preserves information content and semantic distinctions
✅ More precise than generic "contributes to"

This decision prioritizes scientific accuracy and semantic precision over simple agreement with existing pipelines.
