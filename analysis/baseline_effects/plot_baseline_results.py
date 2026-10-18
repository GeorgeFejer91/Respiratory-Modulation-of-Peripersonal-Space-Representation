"""Plot observed baseline-corrected responses with honest measured-range geometry."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy import special, stats

from baseline_effects import OUT, LOCAL, DISTANCES, CELL_NAMES, load_data, cohort_mask, profiles


def main():
    ids, at, baseline, _ = load_data()
    mask = cohort_mask(ids, "primary40")
    ids, at, baseline = ids[mask], at[mask], baseline[mask]
    observed = profiles(at, baseline, "pooled_cp")
    raw = profiles(at, baseline, "raw")
    base_profile = np.nanmean(baseline, axis=-1)
    source = np.load(LOCAL / "joint_logistic_draws.npz")
    step = max(1, source["midpoint_cm"].shape[1]//250)
    def samples(name):
        a = source[name][:, ::step]
        return a.reshape(-1, *a.shape[2:])
    m, sharpness, amp, intercept = [samples(name) for name in ("midpoint_cm", "sharpness_per_cm", "amplitude", "corrected_intercept")]
    width = 1/(4*sharpness)
    grid = np.linspace(10, 100, 241)
    group = np.zeros((len(m), 4, len(grid)))
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "svg.fonttype": "none"})
    count = np.isfinite(at).sum(-1)
    bflat = baseline.reshape(len(ids), 4, -1)
    error = np.sqrt(np.nanvar(at, -1, ddof=1)/count + (np.nanvar(bflat, -1, ddof=1)/np.isfinite(bflat).sum(-1))[..., None])
    with PdfPages(OUT / "participant_curves_native.pdf") as pdf:
        for i, pid in enumerate(ids):
            predicted = 1000*(intercept[:, i, :, None] + amp[:, i, :, None]*(special.expit((grid-m[:, i, :, None])/width[:, i, :, None])-.5))
            group += predicted/len(ids)
            fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
            for c, ax in enumerate(axes.flat):
                low, med, high = np.quantile(predicted[:, c], [.025, .5, .975], axis=0)
                ax.fill_between(grid, low, high, color=colors[c], alpha=.15)
                ax.plot(grid, med, color=colors[c], lw=2)
                ax.errorbar(DISTANCES["registered"], observed[i, c], yerr=error[i, c], fmt="o", color="#222222", capsize=2, markersize=4)
                ax.axhline(0, color="#888888", lw=.7, ls=":")
                ax.set_title(CELL_NAMES[c])
                mq = np.quantile(m[:, i, c], [.025, .5, .975])
                sq = np.quantile(sharpness[:, i, c], [.025, .5, .975])
                ax.text(.03, .97, f"Midpoint {mq[1]:.1f} [{mq[0]:.1f}, {mq[2]:.1f}] cm\nSharpness {sq[1]:.4f} [{sq[0]:.4f}, {sq[2]:.4f}] /cm", transform=ax.transAxes, va="top", fontsize=8,
                    bbox=dict(facecolor="white", alpha=.85, edgecolor="none"))
                ax.set_xlim(8, 102)
            fig.suptitle(f"{pid}: observed responses and joint Bayesian logistic approximation", fontsize=13)
            fig.supxlabel("Registered distance (cm); measured range only", y=.075)
            fig.supylabel("Audio–Tactile minus matched baseline RT (ms)")
            fig.text(.5, .015, "Dots: unsmoothed means ± marginal sampling SE. Band: 95% posterior interval for expected RT.\nBaseline error is shared across distances. Finite model parameters do not establish an observed sigmoid.", ha="center", fontsize=8)
            fig.tight_layout(rect=(.025, .10, 1, .95))
            pdf.savefig(fig)
            if i in (0, 10, 20, 30, 39):
                fig.savefig(LOCAL / (str(pid)+"_atlas_check.png"), dpi=130)
            plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    for c, ax in enumerate(axes.flat):
        low, median, high = np.quantile(group[:, c], [.025, .5, .975], axis=0)
        ax.fill_between(grid, low, high, color=colors[c], alpha=.16, label="95% posterior interval")
        ax.plot(grid, median, color=colors[c], lw=2, label="Joint logistic estimate")
        ax.errorbar(DISTANCES["registered"], observed[:, c].mean(0), yerr=stats.t.ppf(.975, 39)*stats.sem(observed[:, c], axis=0), fmt="o", color="#222222", capsize=3, label="Observed mean ± 95% CI")
        ax.axhline(0, lw=.7, color="#888888", ls=":")
        ax.set_title(CELL_NAMES[c])
        ax.set_xlim(8, 102)
    axes[1, 1].legend(fontsize=8, loc="lower right")
    fig.suptitle("Baseline-corrected responses: 40 independent retained participants")
    fig.supxlabel("Registered distance (cm)", y=.065)
    fig.supylabel("Audio–Tactile minus matched baseline RT (ms)")
    fig.text(.5, .015, "Same axes in all panels. Observations remain unsmoothed. A fitted sigmoid is not evidence that both plateaus were observed.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .09, 1, .95))
    fig.savefig(OUT / "average_curves.png", dpi=180)
    fig.savefig(OUT / "average_curves.pdf")
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharex=True)
    for ax, values, title in zip(axes, (raw, base_profile, observed), ("Audio–Tactile RT", "Baseline RT by nominal label", "AT minus pooled matched baseline")):
        for c, cell in enumerate(CELL_NAMES):
            ax.plot(DISTANCES["registered"], values[:, c].mean(0), marker="o", color=colors[c], label=cell)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Distance / mapped nominal label (cm)")
        ax.set_ylabel("RT (ms)")
    axes[2].legend(fontsize=7)
    fig.text(.5, .015, "Baseline nominal SOA labels have unverified cue-time equivalence. All values are equal-participant means.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, 1))
    fig.savefig(OUT / "baseline_comparison.png", dpi=180)
    fig.savefig(OUT / "baseline_comparison.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
