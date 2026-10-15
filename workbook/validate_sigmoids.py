"""Independent checks of the selected descriptive smoother and sigmoid curves.

Uses statsmodels KernelReg and continuous four-parameter SciPy least_squares,
neither of which is used by the browser's smoothing/profile-grid implementation.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import optimize
from statsmodels.nonparametric.kernel_regression import KernelReg

from descriptive_sigmoid import ProfileGrid, extract_cells, predict, smooth
from paper_analysis import clean
from preparation import FILES, load_pair


def validate(root):
    people,trials=load_pair(*[(root/"data/raw"/name).read_bytes() for name in FILES])
    rows,_,_=clean(people,trials)
    _,cubes,_=extract_cells(rows)
    report=json.loads((root/"results/browser-analysis/analysis_results.json").read_text())
    if report["descriptive_sigmoids"]["selected_method"]!="winsor20/gaussian_constant/0.5/separate":
        raise ValueError("Selected method changed; update the independent reference comparison.")
    x=np.array([0,17/90,40/90,63/90,1.])
    y=cubes["winsor20"].mean(0)
    sy=smooth(x,y,"gaussian_constant",.5)
    pars=ProfileGrid(fine=True).fit(x,sy)
    checks=[]
    for a,b,ps in zip(y,sy,pars):
        reference=KernelReg(a,x,"c",reg_type="lc",bw=[.5]).fit(x)[0]
        fit=optimize.least_squares(lambda q:predict(q[None,:],x)[0]-b,ps,
            bounds=([-2000,0,0,.05],[2000,500,1,1]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=10000)
        if not fit.success:
            raise AssertionError("Independent continuous fit did not converge.")
        checks.append({"kernel_max_error_ms":float(np.max(abs(reference-b))),
            "continuous_reference_midpoint_cm":float(10+90*fit.x[2]),
            "continuous_reference_width_cm":float(90*fit.x[3]),
            "grid_midpoint_cm":float(10+90*ps[2]),"grid_width_cm":float(90*ps[3]),
            "prediction_grid_vs_continuous_max_error_ms":float(np.max(abs(predict(ps[None,:],x)-predict(fit.x[None,:],x))))})
    if max(r["kernel_max_error_ms"] for r in checks)>=1e-10:
        raise AssertionError("Independent kernel estimate differs.")
    if max(r["prediction_grid_vs_continuous_max_error_ms"] for r in checks)>=.015:
        raise AssertionError("Grid resolution is insufficient for curve prediction.")
    return {"status":"passed","kernel_reference":"statsmodels KernelReg local-constant Gaussian, bw=.5",
        "sigmoid_reference":"SciPy least_squares, continuously optimized four parameters","checks":checks}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/full-analysis/sigmoid-validation.json"))
    args=parser.parse_args()
    result=validate(Path(__file__).resolve().parents[1])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Passed independent kernel and continuous sigmoid checks.")
