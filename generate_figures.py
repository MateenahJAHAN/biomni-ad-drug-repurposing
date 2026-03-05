"""Generate publication-quality figures for AD Drug Repurposing submission."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

# ── Shared data ──────────────────────────────────────────────────────────────

drugs = [
    'Minocycline', 'Acetyl-L-carnitine', 'Rapamycin', 'Simvastatin',
    'Pioglitazone', 'Vorinostat', 'Lithium', 'Celecoxib',
    'Metformin', 'Darapladib'
]
scores = [60, 55, 52, 50, 50, 50, 50, 50, 47, 30]
pathways = [
    'Neuroinflammation', 'Energy Metabolism', 'Autophagy/Lysosomal',
    'Lipid Metabolism', 'Neuroinflammation', 'Epigenetic Regulation',
    'Synaptic Maintenance', 'Neuroinflammation', 'Energy Metabolism',
    'Neuroinflammation'
]

pathway_colors = {
    'Neuroinflammation': '#D7263D',
    'Energy Metabolism': '#F57C00',
    'Autophagy/Lysosomal': '#1565C0',
    'Lipid Metabolism': '#F9A825',
    'Epigenetic Regulation': '#7B1FA2',
    'Synaptic Maintenance': '#2E7D32',
}

drug_genes = {
    'Minocycline': ['TREM2', 'CD33', 'INPP5D'],
    'Acetyl-L-carnitine': ['SLC22A5'],
    'Rapamycin': ['BIN1', 'PICALM', 'CD2AP'],
    'Simvastatin': ['APOE', 'ABCA7', 'CLU', 'SORL1'],
    'Pioglitazone': ['TREM2', 'PLCG2'],
    'Vorinostat': ['MEF2C', 'CELF1'],
    'Lithium': ['GSK3B'],
    'Celecoxib': ['PTGS2', 'CD33', 'MS4A6A'],
    'Metformin': ['PRKAB1'],
    'Darapladib': ['PLA2G7', 'ABCA7'],
}

pathway_genes = {
    'Neuroinflammation': ['TREM2', 'CD33', 'INPP5D', 'PLCG2', 'MS4A6A', 'PTGS2', 'PLA2G7'],
    'Autophagy/Lysosomal': ['BIN1', 'PICALM', 'CD2AP'],
    'Lipid Metabolism': ['APOE', 'ABCA7', 'CLU', 'SORL1'],
    'Energy Metabolism': ['SLC22A5', 'PRKAB1'],
    'Epigenetic Regulation': ['MEF2C', 'CELF1'],
    'Synaptic Maintenance': ['GSK3B'],
}

# ── Figure 1: Horizontal bar chart ──────────────────────────────────────────

fig1, ax1 = plt.subplots(figsize=(10, 6))
fig1.patch.set_facecolor('white')

colors = [pathway_colors[p] for p in pathways]
y_pos = np.arange(len(drugs))

bars = ax1.barh(y_pos, scores, color=colors, edgecolor='white', linewidth=0.5, height=0.7)
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f'{i+1}. {d}' for i, d in enumerate(drugs)], fontsize=11, fontweight='medium')
ax1.invert_yaxis()
ax1.set_xlabel('Composite Score', fontsize=12, fontweight='bold')
ax1.set_title('AD Drug Repurposing Candidates — Biomni Agent Discovery',
              fontsize=14, fontweight='bold', pad=15)
ax1.set_xlim(0, 70)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

for bar, score in zip(bars, scores):
    ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             str(score), va='center', fontsize=10, fontweight='bold', color='#333')

legend_patches = [mpatches.Patch(color=c, label=p) for p, c in pathway_colors.items()]
ax1.legend(handles=legend_patches, loc='lower right', fontsize=8.5,
           framealpha=0.9, edgecolor='#ccc', title='Pathway Cluster', title_fontsize=9)

fig1.tight_layout()
fig1.savefig('results/drug_repurposing_scores.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig1)
print('✓ drug_repurposing_scores.png')

# ── Figure 2: Pathway-drug network ──────────────────────────────────────────

G = nx.Graph()

for pw in pathway_genes:
    G.add_node(pw, ntype='pathway')
for d in drugs:
    G.add_node(d, ntype='drug')
all_genes = set()
for genes in drug_genes.values():
    all_genes.update(genes)
for g in all_genes:
    G.add_node(g, ntype='gene')

for d, genes in drug_genes.items():
    for g in genes:
        G.add_edge(d, g, etype='drug-gene')
for pw, genes in pathway_genes.items():
    for g in genes:
        if g in all_genes:
            G.add_edge(pw, g, etype='pathway-gene')

fig2, ax2 = plt.subplots(figsize=(14, 10))
fig2.patch.set_facecolor('white')

pos = nx.spring_layout(G, k=2.2, seed=42, iterations=80)

pathway_nodes = [n for n in G.nodes if G.nodes[n]['ntype'] == 'pathway']
gene_nodes = [n for n in G.nodes if G.nodes[n]['ntype'] == 'gene']
drug_nodes_list = [n for n in G.nodes if G.nodes[n]['ntype'] == 'drug']

pw_edge = [(u, v) for u, v, d in G.edges(data=True) if d['etype'] == 'pathway-gene']
dg_edge = [(u, v) for u, v, d in G.edges(data=True) if d['etype'] == 'drug-gene']

nx.draw_networkx_edges(G, pos, edgelist=pw_edge, edge_color='#aaa', width=1.5, style='solid', ax=ax2)
nx.draw_networkx_edges(G, pos, edgelist=dg_edge, edge_color='#6baed6', width=1.2, style='dashed', ax=ax2)

pw_colors = [pathway_colors.get(n, '#888') for n in pathway_nodes]
nx.draw_networkx_nodes(G, pos, nodelist=pathway_nodes, node_color=pw_colors,
                       node_size=1800, node_shape='s', edgecolors='#333', linewidths=1.5, ax=ax2)
nx.draw_networkx_nodes(G, pos, nodelist=gene_nodes, node_color='#b0d4f1',
                       node_size=500, node_shape='o', edgecolors='#4a90d9', linewidths=1, ax=ax2)

drug_pw_map = dict(zip(drugs, pathways))
drug_c = [pathway_colors.get(drug_pw_map.get(n, ''), '#888') for n in drug_nodes_list]
nx.draw_networkx_nodes(G, pos, nodelist=drug_nodes_list, node_color=drug_c,
                       node_size=700, node_shape='D', edgecolors='#333', linewidths=1, alpha=0.9, ax=ax2)

font_kw = dict(font_size=8, font_weight='bold', ax=ax2)
nx.draw_networkx_labels(G, pos, labels={n: n for n in pathway_nodes}, font_size=9,
                        font_weight='bold', font_color='white', ax=ax2)
nx.draw_networkx_labels(G, pos, labels={n: n for n in gene_nodes}, font_size=7,
                        font_color='#333', ax=ax2)
nx.draw_networkx_labels(G, pos, labels={n: n for n in drug_nodes_list}, font_size=7,
                        font_color='#222', font_weight='bold', ax=ax2)

legend_elements = [
    mpatches.Patch(facecolor='#999', edgecolor='#333', label='Pathway cluster (square)'),
    mpatches.Patch(facecolor='#b0d4f1', edgecolor='#4a90d9', label='AD GWAS risk gene (circle)'),
    mpatches.Patch(facecolor='#ccc', edgecolor='#333', label='Drug candidate (diamond)'),
]
ax2.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.9, edgecolor='#ccc')
ax2.set_title('Pathway–Gene–Drug Network for AD Repurposing Candidates',
              fontsize=14, fontweight='bold', pad=15)
ax2.axis('off')

fig2.tight_layout()
fig2.savefig('results/pathway_cluster_network.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig2)
print('✓ pathway_cluster_network.png')

# ── Figure 3: Heatmap ───────────────────────────────────────────────────────

all_gene_list = sorted(all_genes)
matrix = np.zeros((len(drugs), len(all_gene_list)), dtype=int)
for i, d in enumerate(drugs):
    for g in drug_genes[d]:
        j = all_gene_list.index(g)
        matrix[i, j] = 1

fig3, ax3 = plt.subplots(figsize=(12, 6))
fig3.patch.set_facecolor('white')

from matplotlib.colors import ListedColormap
cmap = ListedColormap(['#f5f5f5', '#1565C0'])

im = ax3.imshow(matrix, cmap=cmap, aspect='auto', interpolation='nearest')

ax3.set_xticks(np.arange(len(all_gene_list)))
ax3.set_yticks(np.arange(len(drugs)))
ax3.set_xticklabels(all_gene_list, fontsize=9, rotation=45, ha='right', fontweight='medium')
ax3.set_yticklabels(drugs, fontsize=10, fontweight='medium')

for i in range(len(drugs)):
    for j in range(len(all_gene_list)):
        if matrix[i, j] == 1:
            ax3.text(j, i, '●', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

ax3.set_title('Drug–Gene Target Relationship Heatmap',
              fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('AD GWAS Risk Genes', fontsize=12, fontweight='bold')
ax3.set_ylabel('Drug Candidates', fontsize=12, fontweight='bold')

ax3.spines[:].set_visible(True)
ax3.spines[:].set_color('#ccc')
ax3.set_xticks(np.arange(len(all_gene_list)) - 0.5, minor=True)
ax3.set_yticks(np.arange(len(drugs)) - 0.5, minor=True)
ax3.grid(which='minor', color='#ddd', linewidth=0.5)
ax3.tick_params(which='minor', bottom=False, left=False)

legend_patches = [mpatches.Patch(facecolor='#1565C0', label='Target relationship'),
                  mpatches.Patch(facecolor='#f5f5f5', edgecolor='#ccc', label='No relationship')]
ax3.legend(handles=legend_patches, loc='upper right', fontsize=9, framealpha=0.9, edgecolor='#ccc')

fig3.tight_layout()
fig3.savefig('results/ad_gwas_gene_drug_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig3)
print('✓ ad_gwas_gene_drug_heatmap.png')

print('\nAll figures generated successfully.')
