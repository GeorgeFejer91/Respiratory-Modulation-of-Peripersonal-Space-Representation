"""Report joint global-time-adjusted PPS contrasts and all their limitations."""
import importlib.util
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy import special, stats

from run import (ROOT, OUT, LOCAL, X, W, EFFECTS, CELL_NAMES, source, prepare, tensors,
                 directional, write_csv)
from session_time import CONFIGS, time_arrays, moments, definition_hash
# Legacy imports prepend other analysis directories containing a namesake report.py.
_spec = importlib.util.spec_from_file_location("trial_cleaning_report", ROOT/"analysis/trial_cleaning/report.py")
_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_report)
table, response = _report.table, _report.response


def main():
    people, trials, eligible, _, ids, _ = source()
    rows, _, _ = prepare(eligible)
    at, baseline = tensors(rows, ids)
    ta, tb = time_arrays(rows, ids, people)
    n, y, ss, ma, ca, aa = moments(at/1000, ta, 2)
    nb, yb, ssb, mb, cb, bb = moments(baseline/1000, tb, 2)
    bflat = baseline.reshape(len(ids), 4, -1)
    observed = np.nanmean(at, -1)-np.nanmean(bflat, -1)[..., None]
    pooled_time = np.sum(nb[..., None]*mb, axis=2)/nb.sum(-1)[..., None]
    error = np.sqrt(np.nanvar(at, -1, ddof=1)/n+np.nanvar(bflat, -1, ddof=1)[..., None]/np.isfinite(bflat).sum(-1)[..., None])
    runs, effect_tables, simple_tables, parameter_tables = [], [], [], []
    time_records, participant_trends, cohort, fit_quality, ppc = [], [], [], [], []
    display, expected_group, adjusted_group = {}, {}, {}
    full_primary = None
    grid = np.linspace(10, 100, 121)
    for name, order, rolling, shape in CONFIGS:
        info = json.loads((OUT / f"{name}_run.json").read_text())
        assert info["definition_sha256"] == definition_hash()
        runs.append(dict(model=name, gate=info["gate"], max_rhat=info["max_rhat"],
            min_bulk_ess=info["min_bulk_ess"], min_tail_ess=info["min_tail_ess"], divergences=info["divergences"]))
        effects = pd.read_csv(OUT / f"{name}_effects.csv")
        effects["gate"] = info["gate"]
        effect_tables.append(effects)
        simple_tables.append(pd.read_csv(OUT / f"{name}_simple_contrasts.csv"))
        parameter_tables.append(pd.read_csv(OUT / f"{name}_participant_parameters.csv"))
        with np.load(LOCAL / f"{name}_draws.npz") as saved:
            values = {q: saved[q].reshape(-1, len(ids), 4) for q in ("midpoint_cm", "width_cm", "sharpness_per_cm",
                "amplitude", "corrected_intercept", "baseline_mean")}
            trend = saved["time_trend"].reshape(-1, len(ids), order)
            assert (values["amplitude"] > 0).all()
            if shape == "visible95":
                assert (special.expit((10-values["midpoint_cm"])/values["width_cm"]) <= .05+1e-12).all()
                assert (special.expit((100-values["midpoint_cm"])/values["width_cm"]) >= .95-1e-12).all()
            for quantity, a in values.items():
                q = np.quantile(a.mean(1), [.025, .5, .975], axis=0)
                for c, cell in enumerate(CELL_NAMES):
                    cohort.append(dict(model=name, cell=cell, quantity=quantity, median=q[1, c], ci_low=q[0, c], ci_high=q[2, c]))
            for j, basis in enumerate(["linear", "quadratic"][:order]):
                for target, a in (("population", saved["beta_time"].reshape(-1, order)[:, j]),
                                   ("finite_cohort", trend[:, :, j].mean(1))):
                    low, med, high = np.quantile(1000*a, [.025, .5, .975])
                    time_records.append(dict(model=name, target=target, basis=basis, median_ms=med,
                        ci_low_ms=low, ci_high_ms=high, probability_negative=float(np.mean(a < 0)), gate=info["gate"]))
                q = np.quantile(1000*trend[:, :, j], [.025, .5, .975], axis=0)
                for i, pid in enumerate(ids):
                    participant_trends.append(dict(model=name, participant_id=pid, basis=basis,
                        median_ms=q[1, i], ci_low_ms=q[0, i], ci_high_ms=q[2, i]))
            mean_trend = trend.mean(0)
            expected_at_reference = 1000*(saved["corrected_curve"].reshape(-1, len(ids), 4, 5).mean(0)+values["baseline_mean"].mean(0)[..., None])
            time_mean = np.einsum("ik,icdk->icd", mean_trend, ma[..., :order])
            residual_ss = ss-2*np.einsum("ik,icdk->icd", mean_trend, ca[..., :order])+np.einsum(
                "ik,il,icdkl->icd", mean_trend, mean_trend, aa[..., :order, :order])
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    total = np.sum(ss[i, c]+n[i, c]*(y[i, c]-n[i, c]@y[i, c]/n[i, c].sum())**2)
                    rss = np.sum(residual_ss[i, c]+n[i, c]*(y[i, c]-time_mean[i, c]-expected_at_reference[i, c]/1000)**2)
                    fit_quality.append(dict(model=name, participant_id=pid, cell=cell,
                        trial_RT_R2_including_time=1-rss/total,
                        midpoint_probability_in_range=float(np.mean((values["midpoint_cm"][:, i, c] >= 10)&(values["midpoint_cm"][:, i, c] <= 100))),
                        midpoint_interval_width_cm=np.ptp(np.quantile(values["midpoint_cm"][:, i, c], [.025, .975])), gate=info["gate"]))
            selected = np.linspace(0, len(trend)-1, min(1200, len(trend)), dtype=int)
            sub = {q: a[selected] for q, a in values.items()}
            sub["time_trend"] = trend[selected]
            display[name] = sub
            expected_group[name] = response(sub, grid).mean(1)
            time_difference = ma[..., :order]-pooled_time[:, :, None, :order]
            detrended = observed[None]-1000*np.einsum("sik,icdk->sicd", trend[selected], time_difference)
            adjusted_group[name] = detrended.mean(1)
            if name == "session_linear_raw_visible95":
                full_primary = {q: values[q].mean(1) for q in ("midpoint_cm", "width_cm")}
            rng = np.random.default_rng(20261620)
            chosen = selected[::max(1, len(selected)//600)]
            for kind, count, actual, means in (("AT", n, y, ma), ("Baseline", nb, yb, mb)):
                gamma = trend[chosen]
                if kind == "AT":
                    curve = saved["corrected_curve"].reshape(-1, len(ids), 4, 5)[chosen]
                    mu = values["baseline_mean"][chosen, ..., None]+curve
                    sigma = saved["sigma_at"].reshape(-1, len(ids))[chosen]
                else:
                    mu = values["baseline_mean"][chosen, ..., None]+np.zeros((len(chosen), len(ids), 4, 5))
                    sigma = saved["sigma_baseline"].reshape(-1, len(ids))[chosen]
                mu = mu+np.einsum("sik,icdk->sicd", gamma, means[..., :order])
                sd = sigma[:, :, None, None]/np.sqrt(count)
                group_se = np.sqrt(np.sum(sd**2, axis=1))/len(ids)
                discrepancy = np.sum(((actual.mean(0)-mu.mean(1))/group_se)**2, axis=(1, 2))
                replicated = mu+rng.normal(size=mu.shape)*sd
                replicated_discrepancy = np.sum(((replicated.mean(1)-mu.mean(1))/group_se)**2, axis=(1, 2))
                ppc.append(dict(model=name, trial_type=kind, draws=len(chosen),
                    mean_profile_tail_probability=float(np.mean(replicated_discrepancy >= discrepancy)), gate=info["gate"]))
    effects = pd.concat(effect_tables, ignore_index=True)
    pd.DataFrame(runs).to_csv(OUT / "session_all_runs.csv", index=False)
    effects.to_csv(OUT / "session_all_effects.csv", index=False)
    pd.concat(simple_tables, ignore_index=True).to_csv(OUT / "session_all_simple_contrasts.csv", index=False)
    pd.concat(parameter_tables, ignore_index=True).to_csv(OUT / "session_all_participant_parameters.csv", index=False)
    write_csv(OUT / "session_time_coefficients.csv", time_records)
    write_csv(OUT / "participant_session_time_parameters.csv", participant_trends)
    write_csv(OUT / "session_cohort_parameters.csv", cohort)
    write_csv(OUT / "session_fit_quality.csv", fit_quality)
    write_csv(OUT / "session_posterior_predictive_checks.csv", ppc)
    gates = {r["model"]: r["gate"] for r in runs}
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    primary_name = "session_linear_raw_visible95"
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    records = []
    for c, ax in enumerate(axes.flat):
        m, w = full_primary["midpoint_cm"][:, c], full_primary["width_cm"][:, c]
        low, high = np.quantile(special.expit((grid-m[:, None])/w[:, None]), [.025, .975], axis=0)
        m0, w0 = np.median(m), np.median(w)
        plugin = special.expit((grid-m0)/w0)
        ax.fill_between(grid, low, high, color=colors[c], alpha=.18)
        ax.plot(grid, plugin, lw=2.5, color=colors[c])
        ax.axvline(m0, ls="--", lw=.8, color=colors[c])
        ax.axhline(.5, ls=":", color="#999999", lw=.7)
        q = np.quantile(m, [.025, .5, .975])
        ax.text(.03, .95, f"Mean midpoint {q[1]:.1f} [{q[0]:.1f}, {q[2]:.1f}] cm", transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(facecolor="white", edgecolor="none", alpha=.85, pad=2))
        ax.set(title=CELL_NAMES[c], xlim=(10, 100), ylim=(-.03, 1.03))
        for j, distance in enumerate(grid):
            records.append(dict(cell=CELL_NAMES[c], distance_cm=distance, median_parameter_sigmoid=plugin[j], ci_low=low[j], ci_high=high[j]))
    fig.suptitle("Session-time-adjusted Bayesian sigmoid approximation")
    fig.supxlabel("Physical distance (cm)", y=.075)
    fig.supylabel("Unit-amplitude model component")
    status = "passed" if gates[primary_name] else "FAILED; display provisional"
    check = next(p for p in ppc if p["model"] == primary_name and p["trial_type"] == "AT")
    extreme = round(check["mean_profile_tail_probability"]*check["draws"])
    fig.text(.5, .012, f"Full-model convergence: {status}. AT mean-profile check: {extreme}/{check['draws']} replicated discrepancies as extreme as observed.\n"
        "Visible S and in-range 5–95% transition are imposed priors. Line: sigmoid at median cohort-mean parameters.\n"
        "Band: 95% interval for that mean-parameter function, using every retained draw. These are not normalized observed RTs.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .13, 1, .95))
    fig.savefig(OUT / "session_sigmoid_curves.png", dpi=180)
    fig.savefig(OUT / "session_sigmoid_curves.pdf")
    plt.close(fig)
    write_csv(OUT / "session_normalized_mean_parameter_curves.csv", records)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    style = [("session_linear_raw_broad", "Linear time / broad", "#215A8E", "-"),
             ("session_linear_roll_broad", "Linear time / rolling", "#387C9B", "--"),
             ("session_linear_raw_visible95", "Linear time / visible S", "#B24C22", "-"),
             ("session_linear_roll_visible95", "Linear time / rolling S", "#D37824", "--"),
             ("session_quadratic_raw_broad", "Quadratic time / broad", "#6C8252", ":")]
    for c, ax in enumerate(axes.flat):
        raw = observed[:, c]
        ax.errorbar(X, raw.mean(0), yerr=stats.sem(raw, axis=0)*stats.t.ppf(.975, len(ids)-1), fmt="o", color="#777777", ms=4, label="Raw matched subtraction ± CI")
        detrended = adjusted_group["session_linear_raw_broad"][:, c]
        q = np.quantile(detrended, [.025, .5, .975], axis=0)
        ax.errorbar(X+1, q[1], yerr=[q[1]-q[0], q[2]-q[1]], fmt="s", color="#215A8E", ms=3, label="Time-standardized means")
        for name, label, color, line in style:
            expected = expected_group[name][:, c]
            if name == "session_linear_raw_broad":
                low, high = np.quantile(expected, [.025, .975], axis=0)
                ax.fill_between(grid, low, high, color=color, alpha=.12)
            ax.plot(grid, expected.mean(0), line, color=color, lw=1.6, label=label+(" *" if not gates[name] else ""))
        ax.axhline(0, color="#BBBBBB", lw=.7)
        ax.set(title=CELL_NAMES[c], xlim=(10, 102), xlabel="Distance (cm)", ylabel="AT − Baseline at common time (ms)")
    axes[0, 0].legend(fontsize=6.5)
    fig.suptitle("Global session-time control: corrected PPS response functions")
    fig.text(.5, .012, "Raw error bars describe variation across participants. Blue adjusted-marker bars describe fitted-trend uncertainty only.\n"
        "Curves are expected responses at centered global time. * Failed full-model gate: provisional. Visible-S geometry is imposed.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .075, 1, .95))
    fig.savefig(OUT / "session_observed_RT.png", dpi=180)
    fig.savefig(OUT / "session_observed_RT.pdf")
    plt.close(fig)

    frame = pd.DataFrame(rows)
    frame = frame[frame.participant_id.isin(ids)].copy()
    frame["rt"] = frame.reaction_time_ms.astype(float)
    frame["global_block"] = (frame.part_number.astype(int)-1)*6+frame.block_number.astype(int)
    orders = {p["participant_id"]: p["condition_order"] for p in people}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, kind in zip(axes[:2], ("Audio-Tactile", "Baseline")):
        a = frame[frame.trial_type == kind].groupby(["participant_id", "global_block"]).rt.mean().unstack("global_block")
        a = a.subtract(a.mean(axis=1), axis=0)
        for order, color in (("Control-Viscereality", "#215A8E"), ("Viscereality-Control", "#B24C22")):
            selected = a.loc[[pid for pid in a.index if orders[pid] == order]]
            mean, se = selected.mean(), selected.sem()
            ax.errorbar(mean.index, mean, yerr=se*stats.t.ppf(.975, selected.count()-1), color=color, marker="o", ms=3, lw=1.2, label=order)
        ax.axvline(6.5, color="#888888", ls=":")
        ax.axhline(0, color="#BBBBBB", lw=.7)
        ax.set(title=kind+" / observed", xlabel="Global block across both interventions", ylabel="RT relative to person's mean across blocks (ms)", xticks=[1, 3, 6, 7, 9, 12])
    u = np.linspace(-.5, .5, 121)
    for name, label, color in (("session_linear_raw_broad", "Shared linear RT trend", "#215A8E"),
                               ("session_quadratic_raw_broad", "Shared quadratic RT trend", "#6C8252")):
        trend = display[name]["time_trend"].mean(1)
        values = 1000*sum(trend[:, j, None]*u[None]**(j+1) for j in range(trend.shape[1]))
        q = np.quantile(values, [.025, .5, .975], axis=0)
        axes[2].fill_between((u+.5)*12+.5, q[0], q[2], color=color, alpha=.15)
        axes[2].plot((u+.5)*12+.5, q[1], color=color, label=label+(" *" if not gates[name] else ""))
    axes[2].axvline(6.5, ls=":", color="#888888")
    axes[2].axhline(0, color="#BBBBBB", lw=.7)
    axes[2].set(title="Estimated additive time component", xlabel="Global block coordinate", ylabel="RT shift from centered session time (ms)", xlim=(.5, 12.5), xticks=[1, 3, 6, 7, 9, 12])
    axes[0].legend(fontsize=7)
    axes[2].legend(fontsize=7)
    fig.suptitle("One continuous session; the clock does not restart at the intervention change")
    fig.text(.5, .012, "Observed panels retain condition/order differences; the model panel shows the additive RT component only.\n"
        "Trial order is a proxy for session progress, not verified elapsed clock time. A trend does not identify fatigue causally.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .08, 1, .92))
    fig.savefig(OUT / "global_time_trend.png", dpi=180)
    fig.savefig(OUT / "global_time_trend.pdf")
    plt.close(fig)

    with PdfPages(OUT / "session_individual_curves.pdf") as pdf:
        for i, pid in enumerate(ids):
            fig, axes = plt.subplots(4, 2, figsize=(12, 14))
            for c, cell in enumerate(CELL_NAMES):
                ax, norm = axes[c//2, c % 2], axes[2+c//2, c % 2]
                ax.errorbar(X, observed[i, c], yerr=error[i, c], fmt="o", color="#777777", ms=3, lw=.7, label="Raw matched means ± SE")
                gamma = display["session_linear_raw_broad"]["time_trend"][:, i, 0]
                adjusted = observed[i, c]-1000*gamma[:, None]*(ma[i, c, :, 0]-pooled_time[i, c, 0])
                ax.plot(X+1, np.median(adjusted, 0), "s", color="#215A8E", ms=3, label="Time-standardized means")
                for name, label, color, line in style:
                    sub = {q: a[:, i, c] for q, a in display[name].items() if q != "time_trend"}
                    ax.plot(grid, response(sub, grid).mean(0), line, color=color, lw=1.2,
                            label=label+(" *" if not gates[name] else ""))
                    norm.plot(grid, special.expit((grid-np.median(sub["midpoint_cm"]))/np.median(sub["width_cm"])), line, color=color, lw=1.2)
                ax.axhline(0, color="#BBBBBB", lw=.7)
                ax.set(title=cell, xlim=(10, 102), xlabel="Distance (cm)", ylabel="Corrected RT at common time (ms)")
                norm.axhline(.5, color="#BBBBBB", ls=":", lw=.7)
                norm.set(title=cell+" / model geometry", xlim=(10, 100), ylim=(-.03, 1.03), xlabel="Distance (cm)", ylabel="Unit-amplitude component")
            axes[0, 0].legend(fontsize=6.5)
            fig.suptitle(f"{pid}: joint global-session-time adjustment and four PPS cells", fontsize=13)
            fig.text(.5, .015, "Both consecutive interventions share the session-wide RT trend; early-block restriction is not a fatigue control.\n"
                "Bottom curves are model geometry at marginal median parameters. Visible S is imposed, not normalized observations.\n"
                "* Failed full-model convergence gate: provisional. Plot lines use 1,200 balanced draws; all tables use every retained draw.", ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .065, 1, .95))
            pdf.savefig(fig)
            if pid == "P000":
                fig.savefig(OUT / "session_individual_example.png", dpi=140)
            plt.close(fig)

    old = pd.read_csv(OUT / "held_distance_predictions.csv")
    reference = old[old.model == "local_raw"]
    predictions = pd.read_csv(OUT / "session_held_distance_predictions.csv")
    assert len(predictions) == 800
    keys = ["held_distance_cm", "participant_id", "cell"]
    ref, pred = reference.set_index(keys).sort_index(), predictions.set_index(keys).sort_index()
    np.testing.assert_allclose(ref[["n_target", "observed_AT_ms"]], pred[["n_target", "observed_AT_ms"]], atol=0)
    combined = pd.concat([reference, predictions], ignore_index=True)
    by_distance = combined.groupby(["model", "held_distance_cm"]).agg(RMSE_ms=("error_ms", lambda a: np.sqrt(np.mean(a*a))),
        log_score=("block_log_predictive_density", "sum"), prediction_gate=("prediction_gate", "all")).reset_index()
    summary = combined.groupby("model").agg(RMSE_ms=("error_ms", lambda a: np.sqrt(np.mean(a*a))),
        log_score=("block_log_predictive_density", "sum"), all_predictive_gates=("prediction_gate", "all")).reset_index()
    by_distance.to_csv(OUT / "session_prediction_by_distance.csv", index=False)
    summary.to_csv(OUT / "session_prediction_summary.csv", index=False)
    primary = effects[effects.quantity.isin(["midpoint_cm_effect", "sharpness_per_cm_effect"])]
    nonzero = primary[(primary.ci_low > 0) | (primary.ci_high < 0)]
    converged = primary[primary.gate]
    converged_nonzero = converged[(converged.ci_low > 0) | (converged.ci_high < 0)]
    coeff = pd.DataFrame(time_records)
    curve_time = coeff[(coeff.model == "session_quadratic_raw_broad") &
                       (coeff.target == "finite_cohort") & (coeff.basis == "quadratic")].iloc[0]
    report = f'''# Main adjustment: continuous session-wide RT trend and PPS

The owner clarified that Control and Viscereality occurred consecutively in one
sitting. **Early blocks of each intervention do not control accumulated time.**
The early subset remains a smaller-trial sensitivity in `RESULTS.md`; it is not a
fatigue exclusion. This subsequent exploratory amendment was specified before its
five fits in `session_specification.json`, after inspecting the earlier results.

The computed readout is **{len(nonzero)}/{len(primary)}** nonzero main parameter
intervals, including **{len(converged_nonzero)}/{len(converged)}** in fits passing
the full convergence gate. Time control has not established a Condition, Phase or
interaction effect on midpoint or sharpness. Forced visible-S geometry remains
a conditional approximation; the mean-profile checks below assess its adequacy
separately from sampling convergence.

## What changed

Use original global trial indices 1–408, spanning parts 1–204 and 205–408, with
`u=(trial_index-1)/(planned_trials-1)-.5`. Do not reset time by condition or
renormalize after trimming/holding out trials. Recorded trial order is a proxy,
not verified elapsed time. Intervention order remains balanced, 20 per sequence.

Each participant has a shared additive RT trend in BOTH AT and Baseline models.
The main trend is linear; quadratic/raw/broad is a fixed sensitivity. Population
coefficients have Normal(0,.2 seconds) priors and participant SDs HalfNormal(.15),
with noncentered participant variation. Signs are unrestricted. Baseline,
intercept/amplitude and shape priors match the preceding sensitivity battery.

This is joint estimation, not fixed-slope preprocessing. Exact within-distance
RT/time cross-products preserve each retained trial's timing. Trend uncertainty
propagates to the four curves, boundary/sharpness and paired contrasts. Rolling
candidates retain the transformed model and overlap covariance. Cutoffs were
not reselected after estimating drift. The corrected function is evaluated at a
common session reference; ideal same-time AT-minus-Baseline cancels shared drift.

## Diagnostics and experimental parameter contrasts

{table(pd.DataFrame(runs))}

All six main contrasts per model, with 95% credible intervals:

{table(primary[['model','quantity','term','posterior_median','ci_low','ci_high','probability_positive','gate']])}

**{len(nonzero)}/{len(primary)}** main parameter intervals exclude zero. Condition
means Viscereality−Control; Phase means Inhale−Exhale; interaction is the difference
of phase differences. These are finite-cohort joint posterior effects with
individual/time uncertainty retained. Failed model gates are inconclusive, not
evidence for zero effects. Among the fits passing the full gate,
**{len(converged_nonzero)}/{len(converged)}** intervals exclude zero. Intervals
containing zero do not establish equivalence or the absence of an effect.
All population coefficients, response effects and simple
contrasts remain in their CSVs. No multiplicity correction or model Bayes factor
was introduced. No pooled-median ANOVA was used as independent evidence.

## Estimated global RT change

{table(coeff)}

The linear coefficient in ms is the modelled start-to-end RT change over the full
planned trial span. The quadratic coefficient multiplies u², whose endpoints are
.25 and whose center is zero; it is not itself an endpoint difference. Negative
linear values mean speeding up. A time effect is an RT-level finding, not a PPS
boundary/sharpness effect. Priors allow slowing, speeding or approximately flat RT.
In the quadratic sensitivity, the finite-cohort quadratic coefficient is
{curve_time.median_ms:.2f} [{curve_time.ci_low_ms:.2f}, {curve_time.ci_high_ms:.2f}] ms.
Its quadratic component alone is therefore
{curve_time.median_ms/4:.2f} [{curve_time.ci_low_ms/4:.2f}, {curve_time.ci_high_ms/4:.2f}] ms
higher at either planned endpoint than at centered time. This is evidence of a
curved time component under that model, not a uniform RT decline or a causal
fatigue diagnosis. The separate linear term remains in the total time function.
`global_time_trend.png` shows observed chronological block trajectories by order
and the estimated additive model component. Stimulus changes, practice, carryover
and fatigue are not causally separable merely by adjusting for these trends.

Posterior-predictive group mean-profile discrepancy tails:

{table(pd.DataFrame(ppc))}

These check AT/Baseline means across nominal distances under the Gaussian model.
Low tails flag unresolved fit; convergence alone does not establish adequacy.
Both visible95 fits returned **0/600** replicated AT mean-profile discrepancies
as extreme as the observed one. This finite Monte Carlo frequency is not an
exact zero probability or a classical p value. It flags poor average-profile
adequacy under those constrained models, despite their successful sampling gates;
the visible S is not validated by the attractive normalized display.
The original baseline-timing uncertainty is not resolved by a time covariate.
`session_fit_quality.csv` reports descriptive trial RT R² INCLUDING the time
predictor. A gain there need not reflect better distance-shape identification.

## Matched prediction after time control

Five additional linear/raw/broad refits use the same held AT trials as the
unadjusted local/raw model. Both filters learn from training RTs only, and the
original global time coordinate stays fixed. Target RTs do not set cutoffs;
their recorded time metadata is used to predict their raw response. Predictive
scores integrate trend, baseline, shape and nuisance uncertainty jointly.
RMSE uses the 800 held participant × cell × distance mean RTs, equally weighted;
the log score integrates all raw held hits jointly within each cell. This is
mean-response prediction error, not individual-trial RMSE.

{table(by_distance)}

{table(summary)}

All matched predictive gates: **{bool(combined.prediction_gate.all())}**. Any failed
fold makes its scores and full aggregate comparison provisional. These within-
cohort checks do not establish new-person generalization, causal identification
or physiological validity. Other time/rolling/visible95 models were not separately
cross-validated. Every failed gate is retained.

## Figures, provenance and scientific status

`session_sigmoid_curves.png` illustrates the mean-parameter linear/raw/visible95
geometry. Its visible S and in-range transition are prior assumptions, not
normalized observations. Its band uses every retained posterior draw.
`session_observed_RT.png` retains raw observations beside time-standardized
summaries and expected corrected functions. Adjusted-marker bars show trend
uncertainty only; raw-marker intervals describe between-person variability.
Blue adjusted markers are displaced +1 cm horizontally for visibility; fitting
and exported distances retain their original values.
`session_individual_curves.pdf` contains all 40 participants and four cells.
Plot curves use 1,200 balanced draws; every exported numerical interval uses all
draws. Nonconverged functions are explicitly marked provisional.

This controls a specified shared additive RT-level time process; it does not
exclude fatigue, carryover, type-specific drift or time-varying PPS shape. Parameter
recovery, repeated full-pipeline coverage and the remaining Q10 model extensions
remain open. Cleaning selection is conditioned on rather than jointly generated.
Raw data, previous results, questionnaires, browser and manuscript remain intact.
The package manifest in `RESULTS.md` covers both this amendment and the eight
unadjusted sensitivities. No significant parameter effect or physiological
measurement is guaranteed by implementing these adjustments.
'''
    (OUT / "SESSION_RESULTS.md").write_text(report)
    print("Session-time report: five fits, five matched folds, forty participant pages.", flush=True)


if __name__ == "__main__":
    main()
