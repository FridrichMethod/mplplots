"""Expression of three genes across four tissues (the script to restyle)."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_theme(style="whitegrid")

rng = np.random.default_rng(7)
tissues = ["Liver", "Kidney", "Heart", "Brain"]
genes = ["GeneA", "GeneB", "GeneC"]
means = {
    "GeneA": [5.1, 3.2, 2.4, 1.1],
    "GeneB": [1.5, 2.8, 4.9, 3.3],
    "GeneC": [2.2, 2.4, 2.1, 6.0],
}

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, gene, letter in zip(axes, genes, "ABC"):
    values = np.array([rng.normal(mean, 0.4, 5) for mean in means[gene]])
    ax.bar(tissues, values.mean(axis=1), yerr=values.std(axis=1, ddof=1) / np.sqrt(5), capsize=4)
    ax.set_title(gene, fontsize=16, fontweight="bold")
    ax.set_ylabel("Expression (log2 TPM)", fontsize=14)
    ax.tick_params(labelsize=12)
    ax.text(-0.15, 1.08, letter, transform=ax.transAxes, fontsize=18, fontweight="bold")

plt.tight_layout()
plt.savefig("expression.png", dpi=300, bbox_inches="tight")
