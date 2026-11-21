"""Demonstrate the Personal style and the figure toolkit: the Personal gallery.

Every figure takes its colours from a small demo palette of ``ColorPair`` roles, is laid out in
round inches with ``grid_inches`` or ``add_axes_inches``, and passes ``assert_figure`` before it
is saved. The data are seeded random numbers, so a rerun writes the same files.
"""

import itertools
from statistics import NormalDist
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from _common import PERSONAL, require_arial, save
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, NullLocator
from numpy.typing import NDArray

import mplplots as mpp
from mplplots.palettes import BLUES, REDS

require_arial()
plt.style.use(PERSONAL)

# A project keeps one palette module of fill and edge pairs (C1); these roles stand in for it.
REFERENCE = mpp.ColorPair(fill="#cccccc", edge="#7a7a7a")
TREATED = mpp.ColorPair(fill="#c7e9c0", edge="#4f9d58")
CONTROL = mpp.ColorPair(fill="#c6dbef", edge="#3182bd")
VARIANT = mpp.ColorPair(fill="#c7c5dc", edge="#634895")
PALETTE = {"reference": REFERENCE, "treated": TREATED, "control": CONTROL, "variant": VARIANT}

if problems := mpp.check_palette(PALETTE):
    raise SystemExit("The demo palette breaks the palette rules:\n" + "\n".join(problems))

# Line widths for curves that share a panel (L4).
CURVE_WIDTH = 1.2
FIT_WIDTH = 1.4
# Bar borders and error bars set their widths explicitly (L8).
BAR_EDGE_WIDTH = 1.0
ERROR_BAR_WIDTH = 0.8
# The scatter recipe (L7).
DOTS: dict[str, Any] = {"s": 22, "linewidths": 0.5, "alpha": mpp.SCATTER_ALPHA}


def bca_interval(
    values: NDArray[np.float64],
    rng: np.random.Generator,
    *,
    resamples: int = 10_000,
    level: float = 0.95,
) -> tuple[float, float]:
    """Return the BCa bootstrap interval of the mean of independent replicates (E3).

    Args:
        values: One value per independent replicate.
        rng: The random generator that draws the resamples.
        resamples: The number of bootstrap resamples.
        level: The coverage of the interval.

    Returns:
        The lower and upper ends of the interval.
    """
    n = values.size
    means = values[rng.integers(0, n, size=(resamples, n))].mean(axis=1)
    normal = NormalDist()
    below = np.clip(np.mean(means < values.mean()), 1 / resamples, 1 - 1 / resamples)
    bias = normal.inv_cdf(float(below))
    # Acceleration from the jackknife means, each leaving one replicate out.
    jackknife = (values.sum() - values) / (n - 1)
    spread = jackknife.mean() - jackknife
    acceleration = float(np.sum(spread**3) / (6.0 * np.sum(spread**2) ** 1.5))
    ends = (normal.inv_cdf((1 - level) / 2), normal.inv_cdf((1 + level) / 2))
    tails = [normal.cdf(bias + (bias + z) / (1 - acceleration * (bias + z))) for z in ends]
    low, high = np.quantile(means, tails)
    return float(low), float(high)


def permutation_p(first: NDArray[np.float64], second: NDArray[np.float64]) -> float:
    """Return the exact two-sided permutation p value for a difference in means.

    Args:
        first: The replicate values of one group.
        second: The replicate values of the other group.

    Returns:
        The fraction of all relabellings whose mean difference is at least the observed one.
    """
    pooled = np.concatenate([first, second])
    labels = np.array(list(itertools.combinations(range(pooled.size), first.size)))
    in_first = np.zeros((len(labels), pooled.size), dtype=bool)
    np.put_along_axis(in_first, labels, values=True, axis=1)
    sums = (in_first * pooled).sum(axis=1)
    differences = sums / first.size - (pooled.sum() - sums) / second.size
    observed = abs(first.mean() - second.mean())
    return float(np.mean(np.abs(differences) >= observed - 1e-12))


def holm(p_values: list[float]) -> list[float]:
    """Return Holm's multiplicity-corrected values for one family of comparisons (E5).

    Args:
        p_values: The uncorrected p values of the family.

    Returns:
        The corrected values, in the order of ``p_values``.
    """
    corrected = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(np.argsort(p_values)):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        corrected[index] = running
    return corrected


# ---------------------------------------------------------------------------
# 1. The comparison plot of the styles, in Personal
# ---------------------------------------------------------------------------
x = np.linspace(0, 10, 50)
fig = plt.figure(figsize=(3, 2.25))
ax = mpp.add_axes_inches(fig, 0.5, 0.4, 2.25, 1.5)
ax.plot(x, np.sin(x), color=BLUES[4], linewidth=CURVE_WIDTH, label=r"$\sin(x)$")
ax.plot(x, np.cos(x), color=REDS[4], linewidth=CURVE_WIDTH, label=r"$\cos(x)$")
mpp.auto_ticks(ax, left=0, right=10)
ax.set_title("Personal + auto_ticks")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
mpp.legend_inches(ax, 2.75, 1.9, loc="upper right", ncols=2)
mpp.assert_figure(fig, warnings_as_errors=True)
save(fig, "personal_style")

# ---------------------------------------------------------------------------
# 2. A 2 by 2 grid with shared axes and one shared y label
# ---------------------------------------------------------------------------
rng = np.random.default_rng(1)
times = np.arange(5.0, 60.0, 10.0)  # sampled inside the axes, so no dot sits on a spine
fine_times = np.linspace(0.0, 60.0, 121)
# Titles need 0.35 in above each row; the right column shares the left column's y ticks.
fig, axes = mpp.grid_inches(
    2, 2, width=1.5, height=1.0, top=0.35, wspace=0.3, hspace=0.35, sharex=True, sharey=True
)
roles = [
    (REFERENCE, "Reference", 40.0),
    (CONTROL, "Control", 25.0),
    (TREATED, "Treated", 12.0),
    (VARIANT, "Variant", 6.0),
]
for ax, (pair, title, tau) in zip(axes, roles):
    for _ in range(3):  # three replicates per condition
        measured = 1.0 - np.exp(-times / tau) + rng.normal(0.0, 0.05, times.size)
        ax.scatter(times, measured, facecolor=pair.fill, edgecolor=pair.edge, **DOTS)
    model = 1.0 - np.exp(-fine_times / tau)  # the curve the replicates scatter around
    ax.plot(fine_times, model, color=pair.edge, linewidth=FIT_WIDTH, alpha=mpp.LINE_ALPHA)
    ax.set_title(title)
axes[0].set(xlim=(0.0, 60.0), ylim=(0.0, 1.2))
axes[0].xaxis.set_major_locator(MultipleLocator(20.0))
axes[0].yaxis.set_major_locator(MultipleLocator(0.5))
for ax in axes[2:]:
    ax.set_xlabel("Time (min)")
mpp.add_shared_ylabel(fig, axes, "Signal (a.u.)")
mpp.assert_figure(fig, warnings_as_errors=True)
save(fig, "personal_grid")

# ---------------------------------------------------------------------------
# 3. Mean +/- SEM profiles, a second state in one hue, and a threshold
# ---------------------------------------------------------------------------
rng = np.random.default_rng(2)
t = np.linspace(0.0, 10.0, 101)
profiles = {
    "Reference": 1.0 + 0.05 * np.sin(t),
    "Treated, rest": 1.0 + 0.4 * (1.0 - np.exp(-t / 2.0)),
    "Treated, stimulated": 1.0 + 1.0 * (1.0 - np.exp(-t / 1.5)),
}
summary: dict[str, tuple[NDArray[np.float64], NDArray[np.float64]]] = {}
for name, profile in profiles.items():  # six replicates per series, reduced to mean and SEM
    gain = rng.normal(1.0, 0.06, (6, 1))
    drift = 0.05 * np.sin(rng.uniform(0.3, 0.8, (6, 1)) * t + rng.uniform(0.0, 2 * np.pi, (6, 1)))
    series = profile * gain + drift
    summary[name] = (series.mean(axis=0), series.std(axis=0, ddof=1) / np.sqrt(6))
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5, right=1.4)
ax.axhline(1.75, label="Threshold", **mpp.REFERENCE_LINE)
mean, sem = summary["Treated, rest"]
mpp.plot_mean_sem(ax, t, mean, sem, fill=TREATED.fill, edge=TREATED.edge, label="Treated, rest")
mean, sem = summary["Treated, stimulated"]
mpp.plot_mean_sem(
    ax,
    t,
    mean,
    sem,
    fill=TREATED.fill,
    edge=TREATED.edge,
    linestyle=mpp.SECONDARY_LINESTYLE,  # the second state of the treated hue (C5)
    label="Treated, stimulated",
)
mean, sem = summary["Reference"]
mpp.plot_mean_sem(
    ax, t, mean, sem, fill=REFERENCE.fill, edge=REFERENCE.edge, label="Reference", zorder=5.0
)  # the reference on top (L6)
ax.set(xlim=(0.0, 10.0), ylim=(0.5, 2.5), xlabel="Time (s)", ylabel="Signal (a.u.)")
ax.yaxis.set_major_locator(MultipleLocator(0.5))
handles, labels = ax.get_legend_handles_labels()
order = [labels.index(name) for name in ("Reference", *list(profiles)[1:], "Threshold")]
mpp.legend_inches(
    ax, 3.2, 1.9, handles=[handles[i] for i in order], labels=[labels[i] for i in order]
)
mpp.assert_figure(fig, warnings_as_errors=True)
save(fig, "personal_mean_sem")

# ---------------------------------------------------------------------------
# 4. Two binned distributions with their legend proxies
# ---------------------------------------------------------------------------
rng = np.random.default_rng(3)
edges = np.linspace(0.0, 6.0, 31)  # a 0.2 bin grid shared by both series
samples = {"Reference": rng.normal(2.2, 0.5, 5000), "Treated": rng.normal(3.6, 0.7, 4000)}
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)
proxies = []
# The reference is drawn on top of the series it overlaps (L6).
for sample, pair, zorder in zip(samples.values(), (REFERENCE, TREATED), (4.0, 2.0)):
    counts, _ = np.histogram(sample, edges)
    proxies.append(
        mpp.plot_distribution(
            ax, edges, counts, sample.size, fill=pair.fill, edge=pair.edge, zorder=zorder
        )
    )
mpp.legend_inches(ax, 3.1, 1.9, loc="upper right", handles=proxies, labels=list(samples))
ax.set(xlim=(0.0, 6.0), ylim=(0.0, 20.0), xlabel="Distance (\u00c5)", ylabel="Percent of samples")
ax.yaxis.set_major_locator(MultipleLocator(5.0))
mpp.assert_figure(fig, warnings_as_errors=True)
save(fig, "personal_distribution")

# ---------------------------------------------------------------------------
# 5. Bars: fill and edge, a hollow second state, 95 % CI and significance stars
# ---------------------------------------------------------------------------
rng = np.random.default_rng(4)
groups = {"Reference": REFERENCE, "Treated": TREATED, "Variant": VARIANT}
group_means = {"Reference": (1.0, 1.05), "Treated": (1.1, 1.9), "Variant": (0.9, 1.25)}
replicates = {
    (group, state): rng.normal(level, 0.15, 6)  # one value per independent replicate (E2)
    for group, levels in group_means.items()
    for state, level in zip(("Resting", "Stimulated"), levels)
}
intervals = {key: bca_interval(values, rng) for key, values in replicates.items()}
q_values = dict(
    zip(
        groups,
        holm([
            permutation_p(replicates[group, "Resting"], replicates[group, "Stimulated"])
            for group in groups
        ]),
    )
)

BAR_WIDTH = 0.36
fig, (ax,) = mpp.grid_inches(width=2.0, height=1.5, right=1.0)
# The individual replicates, as hollow dots (E4).
hollow: dict[str, Any] = {"s": 10, "facecolor": "white", "linewidths": 0.5, "zorder": 3}
for position, (group, pair) in enumerate(groups.items()):
    tops = []
    for offset, state, face in ((-0.2, "Resting", pair.fill), (0.2, "Stimulated", "none")):
        values = replicates[group, state]
        low, high = intervals[group, state]
        ax.bar(
            position + offset,
            values.mean(),
            BAR_WIDTH,
            facecolor=face,
            edgecolor=pair.edge,
            linewidth=BAR_EDGE_WIDTH,
        )
        ax.errorbar(
            position + offset,
            values.mean(),
            yerr=[[values.mean() - low], [high - values.mean()]],
            fmt="none",
            ecolor="black",
            elinewidth=ERROR_BAR_WIDTH,
            capthick=ERROR_BAR_WIDTH,
        )
        ax.scatter(np.full(values.size, position + offset), values, edgecolor=pair.edge, **hollow)
        tops.append(max(high, values.max()))
    bracket = max(tops) + 0.15
    ax.plot(
        [position - 0.2, position - 0.2, position + 0.2, position + 0.2],
        [bracket, bracket + 0.05, bracket + 0.05, bracket],
        color="black",
        linewidth=ERROR_BAR_WIDTH,
    )
    stars = mpp.significance_stars(q_values[group])
    ax.text(position, bracket + 0.05, stars, ha="center", va="bottom")
ax.set_xticks(range(len(groups)), list(groups))
ax.xaxis.set_minor_locator(NullLocator())  # a categorical axis has no minor ticks (L2)
ax.set(xlim=(-0.6, len(groups) - 0.4), ylim=(0.0, 3.0), ylabel="Activity (a.u.)")
ax.yaxis.set_major_locator(MultipleLocator(1.0))
# The state legend copies the reference bars' face, edge and edge width (L8).
states = [
    Patch(facecolor=REFERENCE.fill, edgecolor=REFERENCE.edge, linewidth=BAR_EDGE_WIDTH),
    Patch(facecolor="none", edgecolor=REFERENCE.edge, linewidth=BAR_EDGE_WIDTH),
]
mpp.legend_inches(ax, 2.7, 1.9, handles=states, labels=["Resting", "Stimulated"])
mpp.assert_figure(fig, warnings_as_errors=True)
save(fig, "personal_bars")

print("All Personal examples saved to examples/")
