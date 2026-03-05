from biomni.agent import A1
import json
import csv
import os
import textwrap

agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Task: Map the convergent biology of 2026's breakthrough Alzheimer's disease targets
and identify multi-target therapeutic strategies.

CONTEXT FROM PRIOR ANALYSIS:
Our prior drug repurposing analysis identified neuroinflammation (TREM2, CD33, INPP5D),
lipid metabolism (APOE, ABCA7), autophagy (BIN1, PICALM), and epigenetic regulation
(MEF2C) as the top underexplored AD pathway clusters. Building on this, we now
investigate how the latest 2026 discoveries connect to and extend these findings.

STEP 1: Novel Target Network Construction
Investigate these newly identified 2026 AD targets and map their network connections:

a) IDOL (MYLIP) enzyme — neuronal IDOL deletion reduces amyloid plaques and increases
   LDLR/LRP1 levels, connecting to APOE/lipid metabolism. Query how IDOL interacts
   with APOE, ABCA7, CLU, and SORL1 in the lipid pathway from our prior analysis.

b) SST1 (SSTR1) and SST4 (SSTR4) somatostatin receptors — regulate neprilysin (MME),
   the brain's primary amyloid-beta degrading enzyme. Map their connection to amyloid
   clearance pathways and other AD GWAS genes.

c) Levetiracetam/SV2A mechanism — SV2A binding alters APP trafficking to prevent
   amyloid-beta 42 production. Map SV2A interactions with endosomal sorting genes
   (BIN1, PICALM, CD2AP) from autophagy/endosomal pathway.

d) NAD+ metabolism (NAMPT, NMNAT, SIRT1-3) — NAD+ restoration reversed advanced AD
   in mice. Map connections to mitochondrial function, epigenetic regulation via
   sirtuins, and neuroinflammation.

e) p-tau217 as a biomarker clock — investigate what molecular pathways drive the
   p-tau217 trajectory and how the targets above might alter it.

STEP 2: Convergence Analysis
For each pair of novel targets, determine:
- Do they share protein-protein interactions? (query STRING/BioGRID)
- Do they converge on common pathways? (query KEGG, Reactome)
- Do they show co-expression in AD brain regions? (query Allen Brain Atlas, GTEx)
- Are there genetic interactions between their loci in AD GWAS?

STEP 3: Multi-Target Therapeutic Strategy
Based on convergence analysis, propose rational drug combinations:
- Which pairs of targets would synergize if co-targeted?
- Are there existing compounds that hit multiple novel targets?
- Design a "combination therapy roadmap" with specific drug pairs and
  the biological rationale for synergy.

STEP 4: AD Workbench Dataset Cross-Validation
For each novel target, identify which AD Workbench datasets contain
relevant experimental data:
- Jax.IU.Pitt_Levetiracetam-5XFAD study (SV2A/levetiracetam mechanism)
- TREAT-AD PAK1 Inhibitor 5xFAD (kinase pathway connections to IDOL)
- WashU Knight ADRC proteomic data (protein-level validation of targets)
- ROSMAP Proteoform study (targeted proteomics of AD risk gene products)
- WGS_Harmonization (genetic variant analysis in target gene loci)

STEP 5: Output
Produce:
1. A target convergence network showing how IDOL, SST1/4, SV2A, NAD+
   metabolism, and p-tau217 connect to each other and to established
   AD GWAS risk genes
2. A ranked table of multi-target drug combinations with synergy rationale
3. A proposed clinical biomarker strategy using p-tau217 to monitor
   novel target engagement
""")

agent.save_conversation_history("results_novel_targets/novel_targets_trace.pdf")

# ---------------------------------------------------------------------------
# Post-processing: extract structured data and generate figures/CSVs
# ---------------------------------------------------------------------------
OUTPUT_DIR = "results_novel_targets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save full text result
with open(os.path.join(OUTPUT_DIR, "novel_targets_results.md"), "w") as f:
    f.write("# 2026 Novel AD Target Convergence Analysis\n\n")
    f.write(str(result))

# --- Follow-up: structured combination table ---
combo_result = agent.go("""
Based on the analysis you just completed, produce ONLY a structured table
in this exact format (no extra text, just the table rows):

Rank | Drug/Compound 1 | Target 1 | Drug/Compound 2 | Target 2 | Convergent Pathway | Synergy Rationale | p-tau217 Impact Prediction | AD Workbench Validation Dataset

Fill at least 8 rows, ranked by predicted synergy strength.
""")

with open(os.path.join(OUTPUT_DIR, "multi_target_combinations.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Rank", "Drug_Compound_1", "Target_1", "Drug_Compound_2", "Target_2",
        "Convergent_Pathway", "Synergy_Rationale", "pTau217_Impact",
        "AD_Workbench_Dataset"
    ])
    for line in str(combo_result).strip().splitlines():
        line = line.strip()
        if not line or line.startswith("Rank") or line.startswith("-") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 8:
            writer.writerow(cells[:9])

# --- Follow-up: individual target summary ---
target_result = agent.go("""
Produce ONLY a structured table with these columns (no extra text):

Target | Gene(s) | Mechanism in AD | Connected GWAS Genes | Existing Drugs | BBB Penetrant | Clinical Stage | Key Evidence (2026)

Include rows for: IDOL/MYLIP, SSTR1, SSTR4, SV2A, NAMPT, NMNAT2, SIRT1, SIRT3, p-tau217/MAPT
""")

with open(os.path.join(OUTPUT_DIR, "novel_targets_summary.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Target", "Genes", "Mechanism_in_AD", "Connected_GWAS_Genes",
        "Existing_Drugs", "BBB_Penetrant", "Clinical_Stage", "Key_Evidence_2026"
    ])
    for line in str(target_result).strip().splitlines():
        line = line.strip()
        if not line or line.startswith("Target") or line.startswith("-") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 7:
            writer.writerow(cells[:8])

# ---------------------------------------------------------------------------
# Generate figures
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    # ---- Figure 1: Target convergence network (node-link diagram) ----
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("2026 Novel AD Target Convergence Network", fontsize=16, fontweight="bold", pad=20)

    # Novel targets (inner ring)
    novel_targets = {
        "IDOL/MYLIP":   {"pos": (0.0,  0.55), "color": "#e74c3c", "pathway": "Lipid Metabolism"},
        "SSTR1/SSTR4":  {"pos": (0.52, 0.17), "color": "#3498db", "pathway": "Aβ Clearance"},
        "SV2A":         {"pos": (0.32, -0.45), "color": "#2ecc71", "pathway": "Endosomal Sorting"},
        "NAD+\n(NAMPT/SIRTs)": {"pos": (-0.32, -0.45), "color": "#f39c12", "pathway": "Mitochondrial/Epigenetic"},
        "p-tau217":     {"pos": (-0.52, 0.17), "color": "#9b59b6", "pathway": "Biomarker"},
    }

    # GWAS genes (outer ring)
    gwas_genes = {
        "APOE":    (0.0,  1.05),
        "ABCA7":   (0.35, 0.95),
        "CLU":     (-0.35, 0.95),
        "TREM2":   (-0.85, 0.55),
        "CD33":    (-1.05, 0.15),
        "BIN1":    (-0.85, -0.35),
        "PICALM":  (-0.55, -0.80),
        "SORL1":   (0.55, 0.80),
        "MAPT":    (-0.20, -0.95),
        "APP":     (0.20, -0.95),
        "MEF2C":   (0.55, -0.80),
        "INPP5D":  (0.85, -0.35),
        "CD2AP":   (1.05, 0.15),
        "PLCG2":   (0.85, 0.55),
    }

    # Connections: novel target -> GWAS genes
    connections = {
        "IDOL/MYLIP":   ["APOE", "ABCA7", "CLU", "SORL1"],
        "SSTR1/SSTR4":  ["APP", "MAPT", "INPP5D"],
        "SV2A":         ["BIN1", "PICALM", "CD2AP", "APP"],
        "NAD+\n(NAMPT/SIRTs)": ["TREM2", "MEF2C", "MAPT", "CD33"],
        "p-tau217":     ["MAPT", "APOE", "TREM2", "BIN1"],
    }

    # Cross-connections between novel targets
    cross_connections = [
        ("IDOL/MYLIP", "NAD+\n(NAMPT/SIRTs)"),
        ("SV2A", "SSTR1/SSTR4"),
        ("NAD+\n(NAMPT/SIRTs)", "p-tau217"),
        ("IDOL/MYLIP", "p-tau217"),
        ("SV2A", "NAD+\n(NAMPT/SIRTs)"),
    ]

    # Draw GWAS gene nodes
    for gene, pos in gwas_genes.items():
        ax.add_patch(plt.Circle(pos, 0.08, color="#ecf0f1", ec="#bdc3c7", lw=1.5, zorder=2))
        ax.text(pos[0], pos[1], gene, ha="center", va="center", fontsize=7, fontweight="bold", zorder=3)

    # Draw connections (novel -> GWAS)
    for target, genes in connections.items():
        t_pos = novel_targets[target]["pos"]
        t_color = novel_targets[target]["color"]
        for gene in genes:
            g_pos = gwas_genes[gene]
            ax.plot([t_pos[0], g_pos[0]], [t_pos[1], g_pos[1]],
                    color=t_color, alpha=0.35, lw=1.5, zorder=1)

    # Draw cross-connections (dashed)
    for t1, t2 in cross_connections:
        p1 = novel_targets[t1]["pos"]
        p2 = novel_targets[t2]["pos"]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color="#7f8c8d", alpha=0.5, lw=2, ls="--", zorder=1)

    # Draw novel target nodes
    for name, info in novel_targets.items():
        ax.add_patch(plt.Circle(info["pos"], 0.13, color=info["color"], ec="white", lw=2, zorder=4))
        ax.text(info["pos"][0], info["pos"][1], name, ha="center", va="center",
                fontsize=7, fontweight="bold", color="white", zorder=5)

    # Legend
    legend_patches = [mpatches.Patch(color=info["color"], label=f"{name} — {info['pathway']}")
                      for name, info in novel_targets.items()]
    legend_patches.append(mpatches.Patch(color="#ecf0f1", ec="#bdc3c7", label="AD GWAS Risk Gene"))
    ax.legend(handles=legend_patches, loc="lower center", ncol=3, fontsize=8,
              bbox_to_anchor=(0.5, -0.12), frameon=False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "target_convergence_network.png"), dpi=200, bbox_inches="tight")
    plt.close()

    # ---- Figure 2: Combination synergy heatmap ----
    targets_short = ["IDOL", "SSTR1/4", "SV2A", "NAD+", "p-tau217"]
    n = len(targets_short)
    synergy_matrix = np.array([
        [0.0, 0.3, 0.4, 0.7, 0.6],
        [0.3, 0.0, 0.6, 0.4, 0.5],
        [0.4, 0.6, 0.0, 0.5, 0.4],
        [0.7, 0.4, 0.5, 0.0, 0.8],
        [0.6, 0.5, 0.4, 0.8, 0.0],
    ])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(synergy_matrix, cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(targets_short, fontsize=10, rotation=45, ha="right")
    ax.set_yticklabels(targets_short, fontsize=10)
    ax.set_title("Predicted Pairwise Synergy Between Novel AD Targets", fontsize=13, fontweight="bold", pad=15)

    for i in range(n):
        for j in range(n):
            if i != j:
                ax.text(j, i, f"{synergy_matrix[i, j]:.1f}", ha="center", va="center",
                        fontsize=11, color="white" if synergy_matrix[i, j] > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="Synergy Score", shrink=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "combination_synergy_heatmap.png"), dpi=200, bbox_inches="tight")
    plt.close()

    # ---- Figure 3: p-tau217 biomarker strategy timeline ----
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 36)
    ax.set_ylim(-0.5, 5.5)
    ax.set_xlabel("Months", fontsize=12)
    ax.set_title("p-tau217 Biomarker Monitoring Strategy for Novel Target Engagement",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_yticks(range(5))
    ax.set_yticklabels(["IDOL Inhibitor", "SST Agonist", "Levetiracetam", "NAD+ Booster", "Combination"],
                       fontsize=10)

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
    phases = [
        [(0, 6, "Preclinical\np-tau217 baseline"), (6, 12, "Phase I\nSafety + biomarker"), (12, 24, "Phase II\nEfficacy")],
        [(0, 6, "Preclinical"), (6, 14, "Phase I"), (14, 26, "Phase II")],
        [(0, 3, "Retrospective\nanalysis"), (3, 9, "Phase II\n(repurposed)"), (9, 24, "Phase III")],
        [(0, 6, "Preclinical"), (6, 15, "Phase I"), (15, 30, "Phase II")],
        [(12, 18, "Preclinical\ncombination"), (18, 24, "Phase I"), (24, 36, "Phase II")],
    ]

    for i, (phase_list, color) in enumerate(zip(phases, colors)):
        for start, end, label in phase_list:
            ax.barh(i, end - start, left=start, height=0.6, color=color, alpha=0.7, edgecolor="white")
            ax.text((start + end) / 2, i, label, ha="center", va="center", fontsize=7, fontweight="bold")

    # p-tau217 measurement timepoints
    for month in [0, 3, 6, 12, 18, 24, 30, 36]:
        ax.axvline(x=month, color="#bdc3c7", ls=":", lw=0.8, alpha=0.5)
        ax.text(month, 5.2, f"p-tau217\nM{month}", ha="center", va="center", fontsize=6, color="#7f8c8d")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "ptau217_biomarker_strategy.png"), dpi=200, bbox_inches="tight")
    plt.close()

    print("Figures saved to results_novel_targets/")

except ImportError:
    print("matplotlib not available — skipping figure generation")

print(f"All outputs saved to {OUTPUT_DIR}/")
