"""Independent Bayesian probability checks and actual-browser parity verification."""

import argparse
import io
import json
import zipfile
from hashlib import sha256
from pathlib import Path

import numpy as np
from scipy import special, stats

from bayesian_sigmoid import PRIORS, ShapeGrid, conjugate, weighted_regression
from paper_analysis import clean
from participant_sigmoid import trial_tensor
from preparation import load_pair, local_release_pair


def validate(report):
    people, trials = load_pair(*local_release_pair())
    retained, _, _ = clean(people, trials)
    ids, tensor, _ = trial_tensor(retained)
    assert len(ids) == 42 and tensor.shape[:3] == (42, 4, 5)
    expected = dict(cells=672, model_evidence=2688, prediction=13440, group_contrasts=256, group_cell_summaries=256,
                    associations=1472, joint_moderation=3072, individual_curves=168,
                    average_curves=4, quadrature_checks=168, reliability=80, recovery=120,
                    point_estimate_anova=96)
    assert report["posterior_draws"] == 2000
    assert report["primary_excluded_ids"] == ["P011", "P033"]
    for key, count in expected.items():
        assert len(report[key]) == count, (key, len(report[key]), count)
    errors = []
    # Full covariance Student-t prior prediction independently integrates coefficients and noise.
    for index in np.linspace(0, len(ids)*4-1, 12, dtype=int):
        i, c = divmod(index, 4)
        groups = [v[np.isfinite(v)]/1000. for v in tensor[i, c]]
        counts = np.array([len(v) for v in groups], dtype=float)
        y = np.concatenate(groups)
        sums = np.array([v.sum() for v in groups])
        squares = np.array([v@v for v in groups])
        for prior in PRIORS:
            grid = ShapeGrid(prior)
            for node in (0, len(grid.m)//2, len(grid.m)-1):
                q = grid.basis[node]
                fit = conjugate(counts, sums, squares, q, grid.nuisance)
                x = np.column_stack([np.ones(len(y)), np.repeat(q, counts.astype(int))])
                reference = stats.multivariate_t.logpdf(y, loc=x@np.array([.6, 0.]),
                    shape=.01*(np.eye(len(y))+grid.nuisance*x@x.T), df=4)
                error = abs(float(fit["log_ml"][0])-reference)
                assert error < 1e-8, (index, prior, node, error)
                errors.append(error)
    import statsmodels.api as sm
    rng = np.random.default_rng(204)
    x = np.column_stack([np.ones(40), rng.normal(size=(40, 4))])
    w = rng.exponential(size=(10, 40))
    y = rng.normal(size=(10, 40, 8))
    actual = weighted_regression(x, w, y)
    regression_errors = []
    for draw in range(10):
        for outcome in range(8):
            reference = sm.WLS(y[draw, :, outcome], x, weights=w[draw]).fit().params
            error = float(np.max(np.abs(reference-actual[draw, :, outcome])))
            assert error < 1e-10
            regression_errors.append(error)
    import pandas as pd
    from statsmodels.stats.anova import AnovaRM
    anova_errors, anova_p_errors = [], []
    cells = pd.DataFrame(report["cells"])
    for prior in PRIORS:
        for excluded in ("", "P011,P033", "P011", "P033"):
            data = cells[(cells.prior == prior) & ~cells.participant_id.isin(excluded.split(","))]
            for parameter in ("midpoint_cm", "normalized_steepness_per_cm"):
                reference = AnovaRM(data, parameter, "participant_id", within=["condition", "phase"]).fit().anova_table
                for effect, term in (("Condition", "condition"), ("Phase", "phase"), ("Condition × Phase", "condition:phase")):
                    r, = [r for r in report["point_estimate_anova"] if r["prior"] == prior
                          and r["excluded_ids"] == excluded and r["parameter"] == parameter and r["effect"] == effect]
                    f_error = abs(r["F"]-reference.loc[term, "F Value"])
                    p_error = abs(r["p"]-reference.loc[term, "Pr > F"])
                    assert f_error < 1e-9 and p_error < 1e-9, (prior, excluded, parameter, effect)
                    assert r["df_num"] == reference.loc[term, "Num DF"] == 1
                    assert r["df_den"] == reference.loc[term, "Den DF"] == r["n"]-1
                    anova_errors.append(float(f_error)); anova_p_errors.append(float(p_error))
    grid_errors = {p: max(abs(r[p+"_difference"]) for r in report["quadrature_checks"])
                   for p in ("midpoint_cm", "normalized_steepness_per_cm")}
    assert grid_errors["midpoint_cm"] < .25
    assert grid_errors["normalized_steepness_per_cm"] < 1e-4
    for prior in PRIORS:
        main = [r for r in report["group_contrasts"] if r["prior"] == prior and r["excluded_ids"] == "P011,P033"]
        assert {r["n"] for r in main} == {40}
        for key in ("associations", "joint_moderation"):
            main = [r for r in report[key] if r["prior"] == prior and r["excluded_ids"] == "P011,P033"]
            assert {r["n_complete"] for r in main} == {39}
            assert all(r["valid_draws"] > 1950 for r in main)
    return dict(status="passed", record_counts=expected, student_t_reference_cases=len(errors),
        max_log_marginal_likelihood_error=max(errors), independent_WLS_cases=len(regression_errors),
        max_WLS_coefficient_error=max(regression_errors), quadrature_median_max_difference=grid_errors,
        independent_AnovaRM_terms=len(anova_errors), max_AnovaRM_F_error=max(anova_errors),
        max_AnovaRM_p_error=max(anova_p_errors),
        source_linkage="Both ambiguous records excluded for primary inference; linked copies share latent draws and resampling weights in the provisional full cohort.",
        limits="Probability/numerical verification does not validate the Gaussian model, prior choices, physiological identifiability or causal inference.")


def compare(native, browser):
    errors = []
    def walk(a, b, path=""):
        if isinstance(a, dict):
            assert a.keys() == b.keys(), path
            for key in a:
                walk(a[key], b[key], path+"/"+key)
        elif isinstance(a, list):
            assert len(a) == len(b), path
            for i, (u, v) in enumerate(zip(a, b)):
                walk(u, v, path+"/"+str(i))
        elif isinstance(a, (float, int)) and not isinstance(a, bool):
            error = abs(a-b)
            assert np.isfinite(error) and error <= 1e-8, (path, a, b, error)
            errors.append(error)
        else:
            assert a == b, (path, a, b)
    walk(native, browser)
    return dict(status="passed", numeric_values_compared=len(errors), absolute_tolerance=1e-8,
                max_absolute_numeric_error=max(errors), scope="Every Bayesian result value and label, including prediction, priors, linked-record cohorts, resampled associations/regressions, recovery and curve bands.")


def verified_bundle(path):
    from bayesian_report import SOURCE_FILES
    from preparation import FILES
    data = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert set(manifest["code_sha256"]) == set(SOURCE_FILES)
        assert set(manifest["source_sha256"]) == set(FILES)
        for name, expected in manifest["artifact_sha256"].items():
            assert sha256(archive.read(name)).hexdigest() == expected, name
        for name, expected in manifest["code_sha256"].items():
            assert sha256((Path(__file__).resolve().parent/name).read_bytes()).hexdigest() == expected, name
        for name, expected in manifest["source_sha256"].items():
            assert sha256((Path(__file__).resolve().parent.parent/"data"/"raw"/name).read_bytes()).hexdigest() == expected, name
        report = json.loads(archive.read("bayesian_results.json"))
        assert report["analysis_version"] == manifest["analysis_version"]
    return report, manifest, sha256(data).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("results/bayesian/bayesian_results.json"))
    parser.add_argument("--browser-zip", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".for-ai-local/bayesian-results/independent-validation.json"))
    args = parser.parse_args()
    native = json.loads(args.report.read_text())
    result = validate(native)
    if args.browser_zip:
        browser, manifest, digest = verified_bundle(args.browser_zip)
        assert manifest["runtime"]["execution"] == "browser Pyodide"
        result["browser_native_parity"] = compare(native, browser)
        result["browser_zip_sha256"] = digest
        result["browser_runtime"] = manifest["runtime"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
