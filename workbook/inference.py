"""Browser-compatible statistical routines, validated against independent fits.

Only NumPy/SciPy are needed. Random-intercept ML is profiled exactly using
Woodbury sufficient statistics; no trial-level covariance matrix is allocated.
"""

import math

import numpy as np
from scipy import integrate, linalg, optimize, special, stats


def paired(values, name="contrast", bayes=True):
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]
    result = {"name": name, "n": len(a), "status": "not_estimable"}
    if len(a) < 3 or np.std(a, ddof=1) == 0:
        result["reason"] = "At least three nonconstant participant contrasts are required."
        return result
    mean, sd = float(a.mean()), float(a.std(ddof=1))
    se = sd / np.sqrt(len(a))
    t = mean / se
    half = stats.t.ppf(.975, len(a) - 1) * se
    result.update(status="computed", estimate=mean, se=se, sd=sd, t=t,
                  df=len(a)-1, p=float(2*stats.t.sf(abs(t), len(a)-1)),
                  ci_low=mean-half, ci_high=mean+half, dz=mean/sd,
                  shapiro_p=float(stats.shapiro(a).pvalue))
    if bayes:
        result["bf10_jzs"] = jzs(t, len(a))
        result["bf01_jzs"] = 1/result["bf10_jzs"]
    return result


def jzs(t, n, scale=math.sqrt(.5)):
    """Two-sided one-sample/paired JZS BF10, Cauchy standardized-effect prior.

    Integrate the inverse-gamma(.5,.5) normal-mixture representation in log g.
    The [-40,40] log-scale limits leave negligible prior tail mass for this BF.
    This is not a Bayes factor for a mixed model.
    """
    df = n-1
    def integrand(u):
        log_scale = np.logaddexp(0., math.log(n*scale*scale)+u)
        log_bf = -.5*log_scale + n/2*(math.log1p(t*t/df)-math.log1p(t*t/df*math.exp(-log_scale)))
        log_prior = -.5*math.log(2*math.pi)-.5*u-.5*math.exp(-u)
        return math.exp(log_bf+log_prior)
    value, error = integrate.quad(integrand, -40, 40, epsabs=1e-9, epsrel=1e-8, limit=200)
    if not math.isfinite(value) or value <= 0 or error > max(1e-6, value*1e-5):
        raise ArithmeticError("JZS quadrature did not meet its error tolerance.")
    return float(value)


def sign_flip(values, seed=20261015, samples=19999):
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]
    observed = abs(a.mean())
    if len(a) <= 16:
        integers = np.arange(2**len(a), dtype=np.uint32)
        signs = 2*((integers[:,None] >> np.arange(len(a))) & 1).astype(float)-1
        p = float(np.mean(np.abs(signs@a/len(a)) >= observed-1e-12))
        return {"p": p, "method": "exact sign-flip", "draws": len(integers)}
    rng = np.random.default_rng(seed)
    extreme = 0
    for start in range(0, samples, 1000):
        signs = rng.choice([-1.,1.], size=(min(1000,samples-start),len(a)))
        extreme += int(np.sum(np.abs(signs@a/len(a)) >= observed-1e-12))
    return {"p": (extreme+1)/(samples+1), "method": "Monte Carlo sign-flip",
            "draws": samples, "seed": seed}


def holm(results):
    valid = [r for r in results if r.get("p") is not None and math.isfinite(r["p"])]
    previous = 0.
    for i,r in enumerate(sorted(valid, key=lambda row: row["p"])):
        previous = max(previous, min(1., (len(valid)-i)*r["p"]))
        r["p_holm"] = previous
    return results


def _cache(x, y, groups, z=None):
    cache = []
    for group in sorted(set(groups)):
        mask = groups == group
        xx, yy = x[mask], y[mask]
        zz = np.ones((len(yy),1)) if z is None else z[mask]
        cache.append((len(yy), zz.T@zz, zz.T@xx, zz.T@yy))
    return x.T@x, x.T@y, float(y@y), cache


def mixed_ml(x, y, groups, random_slope=None):
    """Gaussian ML with participant random intercept, optionally random SOA slope.

    The scale parameter is profiled as RSS/n (ML, not REML). Fixed-effect CIs
    use the model-based GLS covariance conditional on the estimated covariance.
    """
    x,y,groups = np.asarray(x,float),np.asarray(y,float),np.asarray(groups)
    n,p = x.shape
    if n <= p or np.linalg.matrix_rank(x) != p or len(set(groups)) < 3:
        raise ValueError("The mixed-model design is not estimable for these inputs.")
    z = None if random_slope is None else np.column_stack([np.ones(n),random_slope])
    xtx,xty,yty,cache = _cache(x,y,groups,z)

    def profile(g, details=False):
        a,b,c,logdet = xtx.copy(),xty.copy(),yty,0.
        for _,ztz,ztx,zty in cache:
            matrix = np.eye(g.shape[0])+g@ztz
            sign,ld = np.linalg.slogdet(matrix)
            if sign <= 0:
                return math.inf
            w = np.linalg.solve(matrix,g)
            a -= ztx.T@w@ztx
            b -= ztx.T@w@zty
            c -= float(zty@w@zty)
            logdet += ld
        try:
            beta = np.linalg.solve(a,b)
            rss = c-float(beta@b)
            if rss <= 0:
                return math.inf
            variance = rss/n
            ll = -.5*(n*(math.log(2*math.pi*variance)+1)+logdet)
            if details:
                covariance = variance*np.linalg.inv(a)
                return ll,beta,covariance,variance
            return -ll
        except np.linalg.LinAlgError:
            return math.inf

    if z is None:
        optimum = optimize.minimize_scalar(lambda u: profile(np.array([[math.exp(u)]])),
            bounds=(-20,20),method="bounded",options={"xatol":1e-9})
        candidates = [(profile(np.array([[0.]])),np.array([[0.]]),True,"variance boundary"),
                      (optimum.fun,np.array([[math.exp(optimum.x)]]),bool(optimum.success),"profile ML scalar")]
    else:
        intercept = mixed_ml(x,y,groups)
        def covariance(theta):
            lower = np.array([[math.exp(theta[0]),0.],[theta[1],math.exp(theta[2])]])
            return lower@lower.T
        initial = [math.log(max(intercept["relative_covariance"][0][0],1e-6))*.5,0.,-1.5]
        candidates = []
        for method in ("L-BFGS-B","Powell"):
            fit = optimize.minimize(lambda theta: profile(covariance(theta)), initial,
                method=method,bounds=[(-12,12),(-10,10),(-12,12)],
                options={"maxiter":1000,"ftol":1e-10})
            candidates.append((float(fit.fun),covariance(fit.x),bool(fit.success),method))
        boundary = np.array([[intercept["relative_covariance"][0][0],0.],[0.,0.]])
        candidates.append((profile(boundary),boundary,True,"zero slope variance boundary"))
    finite = [c for c in candidates if c[2] and math.isfinite(c[0])]
    if not finite:
        raise ArithmeticError("No converged finite ML solution; no model substitution was made.")
    _,g,_,method = min(finite,key=lambda item:item[0])
    ll,beta,covariance,variance = profile(g,True)
    se = np.sqrt(np.maximum(0,np.diag(covariance)))
    return {"ll":float(ll),"beta":beta,"se":se,"covariance":covariance,
            "residual_variance":float(variance),"relative_covariance":g.tolist(),
            "n":n,"participants":len(cache),"fixed_parameters":p,
            "converged":True,"optimizer":method,
            "variance_boundary":bool(np.min(np.linalg.eigvalsh(g))<1e-6)}


def mixed_comparison(x,y,groups,names,drop,random_slope=None,name="interaction"):
    keep = [i for i in range(len(names)) if i not in drop]
    full = mixed_ml(x,y,groups,random_slope)
    reduced = mixed_ml(x[:,keep],y,groups,random_slope)
    statistic = 2*(full["ll"]-reduced["ll"])
    if statistic < -1e-5:
        raise ArithmeticError("Nested ML likelihoods are inconsistent; inspect optimization.")
    statistic = max(0.,statistic)
    coefficients = []
    for label,beta,se in zip(names,full["beta"],full["se"]):
        coefficients.append({"term":label,"estimate":float(beta),"se":float(se),
            "ci_low":float(beta-1.95996398454*se),"ci_high":float(beta+1.95996398454*se)})
    return {"name":name,"status":"computed","n":full["n"],"participants":full["participants"],
        "lr":statistic,"df":len(drop),"p":float(stats.chi2.sf(statistic,len(drop))),
        "ll_full":full["ll"],"ll_reduced":reduced["ll"],"coefficients":coefficients,
        "converged":full["converged"] and reduced["converged"],
        "optimizer_full":full["optimizer"],"optimizer_reduced":reduced["optimizer"],
        "variance_boundary":full["variance_boundary"],
        "relative_covariance":full["relative_covariance"],
        "ci_method":"normal Wald, model-based GLS conditional on estimated variance"}


def cluster_regression(x,y,groups,names,binomial=False,name="cluster regression"):
    x,y,groups = np.asarray(x,float),np.asarray(y,float),np.asarray(groups)
    n,p = x.shape
    if np.linalg.matrix_rank(x)!=p or len(set(groups))<3:
        raise ValueError("Cluster regression requires a full-rank design and at least three participants.")
    if binomial:
        def nll(beta):
            linear = x@beta
            return float(np.sum(np.logaddexp(0.,linear)-y*linear))
        fit = optimize.minimize(nll,np.zeros(p),jac=lambda b:x.T@(special.expit(x@b)-y),
            hess=lambda b:x.T@((special.expit(x@b)*(1-special.expit(x@b)))[:,None]*x),
            method="Newton-CG",options={"xtol":1e-9,"maxiter":200})
        if not fit.success:
            raise ArithmeticError("The binomial model did not converge.")
        beta = fit.x
        probability = special.expit(x@beta)
        bread = np.linalg.inv(x.T@((probability*(1-probability))[:,None]*x))
        residual = y-probability
    else:
        beta = np.linalg.lstsq(x,y,rcond=None)[0]
        bread = np.linalg.inv(x.T@x)
        residual = y-x@beta
    scores = np.array([x[groups==g].T@residual[groups==g] for g in sorted(set(groups))])
    count = len(scores)
    covariance = count/(count-1)*(n-1)/(n-p)*bread@(scores.T@scores)@bread
    se = np.sqrt(np.maximum(0,np.diag(covariance)))
    coefficients = []
    for label,b,s in zip(names,beta,se):
        coefficients.append({"term":label,"estimate":float(b),"se":float(s),
            "ci_low":float(b-1.95996398454*s),"ci_high":float(b+1.95996398454*s),
            "p":float(2*stats.norm.sf(abs(b/s))) if s>0 else None})
    return {"name":name,"status":"computed","n":n,"participants":count,
        "coefficients":coefficients,"correction":"G/(G-1)*(n-1)/(n-p)",
        "reference_distribution":"normal Wald","family":"binomial logit" if binomial else "Gaussian OLS"}


def repeated_anova(cell_array):
    """Complete-subject 2x2x5 univariate RM ANOVA with per-effect GG correction."""
    a = np.asarray(cell_array,float)
    n = len(a)
    if n<3 or a.shape[1:]!=(2,2,5):
        raise ValueError("The repeated-measures ANOVA needs at least three complete 2x2x5 subjects.")
    contrasts = [linalg.helmert(2),linalg.helmert(2),linalg.helmert(5)]
    means = [np.ones((1,k))/np.sqrt(k) for k in (2,2,5)]
    out = []
    for active in ((0,),(1,),(2,),(0,1),(0,2),(1,2),(0,1,2)):
        basis = [contrasts[i] if i in active else means[i] for i in range(3)]
        matrix = np.kron(np.kron(basis[0],basis[1]),basis[2])
        scores = a.reshape(n,-1)@matrix.T
        q = scores.shape[1]
        mean = scores.mean(axis=0)
        ss_error = float(np.sum((scores-mean)**2))
        if ss_error<=0:
            continue
        f = float(n*(mean@mean)/(ss_error/(n-1)))
        covariance = np.atleast_2d(np.cov(scores,rowvar=False,ddof=1))
        epsilon = float(np.clip(np.trace(covariance)**2/(q*np.trace(covariance@covariance)),1/q,1))
        out.append({"effect":" × ".join(("Condition","Phase","SOA")[i] for i in active),
            "n":n,"F":f,"df1":q,"df2":q*(n-1),"epsilon_GG":epsilon,
            "p_uncorrected":float(stats.f.sf(f,q,q*(n-1))),
            "p_GG":float(stats.f.sf(f,q*epsilon,q*(n-1)*epsilon))})
    return out
