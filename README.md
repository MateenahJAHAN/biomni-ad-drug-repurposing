# AD Drug Repurposing via Biomni Agent

## Discovery

AI agent-driven identification of FDA-approved drugs with novel mechanistic rationale for Alzheimer's disease repurposing, targeting underexplored pathways including neuroinflammation, lipid metabolism, and autophagy.

## Method

- **Framework:** Biomni v0.0.6 (Stanford SNAP Lab)
- **LLM:** Claude Sonnet 4 (claude-sonnet-4-20250514) via Anthropic API
- **Databases queried:** GWAS Catalog, OpenTargets, UniProt, DrugBank
- **AD Workbench reference datasets:** TREAT-AD PAK1 Inhibitor 5xFAD Study, TREAT-AD BV2 BioHvY Study, WashU Knight ADRC proteomic data

## Reproduction

```bash
git clone https://github.com/MateenahJAHAN/biomni-ad-drug-repurposing.git
cd biomni-ad-drug-repurposing
# Install Biomni (see https://github.com/snap-stanford/Biomni for setup)
export ANTHROPIC_API_KEY="your-key"
python run_ad_repurposing.py
```

## Results

*To be populated after agent run completes — ranked drug candidates table.*

## Experimental Validation Proposals

*To be populated after agent run completes — proposed wet-lab protocols.*
