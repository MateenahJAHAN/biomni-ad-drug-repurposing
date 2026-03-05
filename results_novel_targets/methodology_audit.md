# Methodology Audit — 2026 Novel AD Targets Analysis

## Execution Status

**CRITICAL: This script (`run_ad_novel_targets_2026.py`) has NOT been successfully
executed.** The Biomni agent calls failed due to missing API credentials in the
execution environment. This audit is therefore a **pre-execution analysis** of
what the script would do, and a transparency assessment of its design.

## What Would Run (If Executed)

The script makes **3 sequential Biomni agent calls** plus local figure generation:

### Agent Call 1: Main Analysis (line 9)

**Prompt requests the agent to:**
1. Query IDOL/MYLIP, SSTR1, SSTR4, SV2A, NAD+ metabolism genes
2. Map protein-protein interactions via STRING/BioGRID
3. Query KEGG, Reactome for pathway convergence
4. Query Allen Brain Atlas, GTEx for co-expression
5. Cross-validate against AD Workbench datasets

**What would ACTUALLY happen (based on prior trace analysis):**

Biomni's `A1.go()` would:
1. Use the tool retriever to select relevant database tools
2. The LLM agent would write Python code calling Biomni's database wrappers
3. Available real API tools: `query_gwas_catalog`, `query_opentarget`, `query_chembl`, `query_pubchem`

**What would NOT happen:**
- STRING/BioGRID: Biomni has BioGRID parquet data in its data lake (downloaded as
  `affinity_capture-ms.parquet`) but does NOT have a `query_string` function.
  The agent might load the local parquet file or skip PPI analysis entirely.
- KEGG/Reactome: No dedicated Biomni query functions exist for these databases.
  The agent would likely use OpenTargets pathway data or reason from training knowledge.
- Allen Brain Atlas/GTEx: No Biomni query functions exist. The agent would use
  LLM knowledge for co-expression claims.
- AD Workbench: These are referenced for context but Biomni has no API to query
  AD Knowledge Portal programmatically.

### Agent Call 2: Combination Table (line 88)

Asks the agent to produce a structured table of drug combinations.
**This is entirely LLM-synthesized** — it asks the agent to format results from
Call 1, which itself would be a mix of API data and LLM reasoning.

### Agent Call 3: Target Summary Table (line 113)

Asks the agent to produce a structured target summary.
**This is entirely LLM-synthesized** — same pattern as Call 2.

### Local Figure Generation (lines 138-306)

Three matplotlib figures are generated with **entirely hardcoded data**:

#### Figure 1: Target Convergence Network
- Node positions, colors, and connections are all hardcoded in Python dictionaries
- The connections (e.g., IDOL→APOE, SV2A→BIN1) are **author-asserted**, not
  derived from any database query
- **Source: LLM/author knowledge, not API data**

#### Figure 2: Combination Synergy Heatmap
- The synergy matrix is a hardcoded 5×5 numpy array:
  ```python
  synergy_matrix = np.array([
      [0.0, 0.3, 0.4, 0.7, 0.6],
      [0.3, 0.0, 0.6, 0.4, 0.5],
      ...
  ])
  ```
- **These numbers are fabricated** — they are not derived from any computational
  model, experimental data, or database query
- **Source: LLM-generated placeholder values**

#### Figure 3: p-tau217 Biomarker Timeline
- Clinical phase timelines are hardcoded tuples
- **Source: LLM-generated estimates, not from clinical trial databases**

## Database Availability Assessment

Based on what Biomni v0.0.8 actually provides:

| Requested Database | Biomni Tool Available? | Would Make Real API Call? |
|-------------------|----------------------|-------------------------|
| GWAS Catalog | Yes (`query_gwas_catalog`) | Yes — EBI REST API |
| OpenTargets | Yes (`query_opentarget`) | Yes — GraphQL API |
| ChEMBL | Yes (`query_chembl`) | Yes — EBI REST API |
| STRING | No dedicated function | No — would use LLM knowledge |
| BioGRID | Local parquet only | Partial — local data, no API |
| KEGG | No | No — would use LLM knowledge |
| Reactome | No | No — would use LLM knowledge |
| Allen Brain Atlas | No | No — would use LLM knowledge |
| GTEx | No | No — would use LLM knowledge |
| AD Workbench/AD KP | No | No — would use LLM knowledge |
| PubMed | Yes (`query_pubmed`) | Depends on pymed install |
| DrugBank | No | No — ChEMBL used instead |

## Predicted Data Provenance (If Script Runs Successfully)

| Output Component | Likely Source | Confidence |
|-----------------|-------------|------------|
| IDOL/MYLIP gene associations | OpenTargets API (real) + LLM | Medium |
| SSTR1/SSTR4 pathway mapping | Mostly LLM reasoning | Low |
| SV2A-endosomal gene connections | OpenTargets API + LLM | Medium |
| NAD+ metabolism network | Mostly LLM reasoning | Low |
| p-tau217 pathway analysis | Entirely LLM reasoning | Low |
| Protein-protein interactions | BioGRID parquet (partial) or LLM | Low-Medium |
| Pathway convergence | LLM reasoning (no KEGG/Reactome API) | Low |
| Co-expression data | LLM reasoning (no GTEx/Allen API) | Low |
| Drug combination rankings | LLM reasoning | Low |
| Synergy heatmap values | Hardcoded placeholders | None — fabricated |
| Clinical timeline | LLM reasoning | Low |
| AD Workbench cross-references | LLM reasoning | Low |

## Recommendations

1. **Do not present the synergy heatmap as data-driven** — the values are
   hardcoded placeholders with no computational basis
2. **Do not claim STRING/BioGRID/KEGG/Reactome/GTEx were queried** — Biomni
   lacks API tools for these databases
3. **If the script is run successfully**, examine the trace file to determine
   which API calls actually returned data vs where the agent fell back to
   LLM knowledge (same pattern as the prior analysis)
4. **The figures should be labeled** as "illustrative" or "hypothesis-based"
   rather than "data-derived"

## Conclusion

This script is designed as an **LLM-guided hypothesis generation tool** that
would use selective database grounding where Biomni APIs are available. The
majority of the novel target analysis (convergence, synergy, clinical strategy)
would be LLM-synthesized even if the script runs successfully, because Biomni
lacks API tools for most of the requested databases (STRING, KEGG, Reactome,
GTEx, Allen Brain Atlas, AD Workbench).

The three figures are generated from hardcoded data regardless of whether the
Biomni agent runs, making them illustrative diagrams rather than data
visualizations.
