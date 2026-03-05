# Methodology Audit — Data Provenance & Transparency

## Overview

This document provides a detailed audit of what data in this analysis came from
real database queries versus LLM (Claude) reasoning. The Biomni framework uses a
hybrid approach: an LLM generates API queries from natural language, then executes
real HTTP calls against biological databases. However, not all claims in the final
output trace back to API responses.

## Databases with Verified API Calls

### 1. GWAS Catalog (EBI)

**Status: REAL DATA**

- **Endpoint:** `https://www.ebi.ac.uk/gwas/rest/api/`
- **Calls made:**
  - `query_gwas_catalog("Alzheimer's disease GWAS associations and risk loci")`
    → `findByEfoTrait` → returned empty (no associations matched)
  - `query_gwas_catalog("Find GWAS studies for Alzheimer disease and dementia")`
    → `findByEfoTrait` → returned real study metadata (GCST001947, GCST001963, etc.)
  - Local data lake: `gwas_catalog.pkl` → 622,784 total entries → 3,258 AD entries → 2,331 unique genes
- **Raw data evidence:** Study accession IDs, PubMed IDs (23565137, 23571587),
  sample sizes, and ancestry information all verifiable against EBI GWAS Catalog

### 2. OpenTargets

**Status: REAL API CALLS (LLM-generated GraphQL)**

- **Endpoint:** `https://api.platform.opentargets.org/api/v4/graphql`
- **Genes queried:** APOE, TREM2, CD33, MS4A6A, CD2AP, EPHA1, BIN1, CLU
- **Method:** Claude generates a GraphQL query from natural language prompt →
  real POST request to OpenTargets API
- **Caveat:** The LLM generates the GraphQL query, so the quality of data
  returned depends on whether Claude produces a valid, well-targeted query.
  The trace shows `✓ Retrieved data for {gene}` but does not display the
  full API response for each gene.

### 3. ChEMBL (EBI)

**Status: REAL API CALLS**

- **Endpoint:** `https://www.ebi.ac.uk/chembl/api/data`
- **Queries made:**
  - Drug mechanism queries: Acetylcarnitine, Pilsicainide, Darapladib
  - Target protein queries: TREM2, CD33, ABCA7, SORL1, PLCG2
- **Method:** LLM generates query parameters → real GET/POST to ChEMBL REST API

### 4. TxGNN (Local Model)

**Status: REAL COMPUTATIONAL PREDICTION**

- **Method:** `retrieve_topk_repurposing_drugs_from_disease_txgnn()`
- **Input:** disease_name="Alzheimer's disease", k=20
- **Output:** 20 drugs with prediction scores (post-sigmoid). Key results:
  - Tacrine: 0.9961 (known AD drug — validates model)
  - Rivastigmine: 0.9956 (known AD drug — validates model)
  - Acetylcarnitine: 0.9953 (novel candidate)
  - Galantamine: 0.9909 (known AD drug — validates model)
  - Darapladib: 0.9825 (novel candidate)
- **Note:** TxGNN is a pre-trained graph neural network from Stanford SNAP Lab.
  These are genuine model predictions, not LLM-generated.

### 5. DisGeNET (Data Lake)

**Status: REAL DATA (downloaded parquet file)**

- Downloaded `DisGeNET.parquet` (2.95 MB) from Biomni data lake
- Used as a local reference dataset

## Agent-Synthesized Content (LLM Reasoning)

The following elements in the final output were **not extracted from API responses**
but were composed by the Claude agent from its biomedical training knowledge:

### Final Top 10 Drug List (lines 865-936 of trace)

After PubMed queries failed (see below), the agent hardcoded the drug candidate
dictionary directly in Python:

```python
# Based on literature and known mechanisms, let's compile a comprehensive list
comprehensive_candidates = {
    'Acetyl-L-carnitine': {
        'mechanism': 'Mitochondrial function, lipid metabolism',
        'bbb_penetration': 'High',
        ...
    },
    'Minocycline': { ... },
    ...
}
```

The drug names, mechanisms, BBB penetration ratings, pathways, and rationales
were written by the LLM, not extracted from database responses.

### Pathway Categorization (line 662 of trace)

```python
pathway_categories = {
    'neuroinflammation': ['TREM2', 'CD33', 'MS4A6A', 'CR1', 'INPP5D', 'PLCG2'],
    'lipid_metabolism': ['APOE', 'CLU', 'ABCA7', 'SORL1'],
    ...
}
```

While these gene-pathway assignments are well-established in the literature,
they were hardcoded by the LLM rather than derived from a pathway database query.

### Composite Scores

The final scores (Minocycline 60, Acetyl-L-carnitine 55, etc.) were computed by
an LLM-authored scoring function with LLM-assigned inputs, not from any external
scoring system.

### Experimental Validation Proposals

Cell lines, dose ranges, assay types, and timelines are LLM-generated suggestions
based on standard practices in the field.

## Databases NOT Queried

### STRING/BioGRID
- **Status: NEVER CALLED**
- Despite the prompt requesting protein-protein interaction queries, the agent
  never imported or called `query_string` or `query_biogrid` functions.
- No PPI data was used in the analysis.

### PubMed
- **Status: FAILED (all 5 calls)**
- Error: `No module named 'pymed'`
- The agent attempted literature searches for:
  - FDA-approved anti-inflammatory drugs that cross BBB
  - FDA-approved cholesterol-lowering drugs with neuroprotective effects
  - FDA-approved autophagy modulators
  - FDA-approved drugs targeting complement system
  - FDA-approved epigenetic modulators for neurodegeneration
- All returned errors. **No literature data was retrieved.**

### DrugBank
- **Status: NOT AVAILABLE**
- `query_drugbank` does not exist in Biomni's tool suite.
- ChEMBL was used as the alternative drug database.

### UniProt
- **Status: IMPORTED BUT NOT CALLED**
- `query_uniprot` was imported but no direct calls appear in the trace.

## How Biomni's Database Tools Work

Biomni uses a **two-stage hybrid approach** for all database queries:

1. **Stage 1 — LLM query generation:** Claude receives a natural language prompt
   plus an API schema (stored as `.pkl` files). It generates the appropriate
   REST/GraphQL query parameters.
2. **Stage 2 — Real HTTP execution:** The generated query is executed against the
   actual database API endpoint using the `requests` library.

This means:
- The API calls are **real** — they hit live endpoints and return real data
- The **quality** of results depends on whether Claude generates a valid query
- If the LLM generates a poorly formed query, the API may return empty or
  irrelevant results (as happened with the first GWAS Catalog call)

## Conclusion

This analysis is best characterized as an **LLM-guided hypothesis generation
pipeline with selective database grounding**:

| Component | Source | Confidence |
|-----------|--------|------------|
| AD risk gene landscape | GWAS Catalog (real data) | High |
| Gene-pathway-drug network topology | OpenTargets + ChEMBL (real APIs) | Medium |
| Drug repurposing predictions | TxGNN (real model) | High |
| Final drug ranking & scores | LLM reasoning | Low — requires validation |
| BBB penetration ratings | LLM reasoning | Low — requires verification |
| Mechanism rationales | LLM reasoning | Medium — consistent with literature |
| Experimental proposals | LLM reasoning | Medium — standard protocols |
| Protein-protein interactions | Not queried | N/A |
