"""MFIN 4338 Empirical Methods in Finance - Problem Set 1 (Fall 2026)
Run: python hw1.py   (expects data/data_assignment1.xlsx and data/pension.dta)
Figures are saved to figs/, all numerical results are printed to stdout.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.stattools import jarque_bera

os.makedirs("figs", exist_ok=True)
pd.set_option("display.width", 200, "display.float_format", lambda v: f"{v:,.4f}")

# =====================================================================
# QUESTION 1
# =====================================================================
print("=" * 70, "\nQUESTION 1\n", "=" * 70)

# (a) Import ----------------------------------------------------------
df = pd.read_excel("data/data_assignment1.xlsx", sheet_name="stock_monthly")
df = df.set_index("DATE").sort_index()
names = {"VWRET": "VW index", "EWRET": "EW index", "COCACOLA": "Coca-Cola (KO)",
         "MICROSOFT": "Microsoft (MSFT)", "EXXON": "ExxonMobil (XOM)"}
cols = list(names)
print("(a) shape:", df.shape, "| range:", df.index.min().date(), "to", df.index.max().date())

# (b) Simple -> log returns: r_log = ln(1 + r_simple) ------------------
lr = np.log1p(df[cols])

# (c) Time-series plots (simple vs log, one figure per series) --------
for c in cols:
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.plot(df.index, df[c], lw=1, label="Simple return")
    ax.plot(lr.index, lr[c], lw=1, alpha=.8, label="Log return")
    ax.axhline(0, color="k", lw=.5)
    ax.set_title(f"{names[c]}: monthly simple vs log returns"); ax.legend()
    fig.tight_layout(); fig.savefig(f"figs/q1c_{c}.png", dpi=130); plt.close(fig)
print("(c) max |simple-log| gap by series:\n", (df[cols] - lr).abs().max())
print("    worst months (VW):", lr["VWRET"].nsmallest(3).round(4).to_dict())

# (d) Correlation matrix ---------------------------------------------
print("\n(d) Correlation matrix of log returns:\n", lr.corr())

# (e) Scatterplots vs VWRET ------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
for ax, c in zip(axs, ["COCACOLA", "MICROSOFT", "EXXON"]):
    ax.scatter(lr["VWRET"], lr[c], s=9, alpha=.6)
    b = np.polyfit(lr["VWRET"], lr[c], 1)
    xs = np.linspace(lr["VWRET"].min(), lr["VWRET"].max(), 50)
    ax.plot(xs, np.polyval(b, xs), "r"); ax.set_xlabel("VW index log return")
    ax.set_ylabel(f"{names[c]} log return"); ax.set_title(names[c])
fig.tight_layout(); fig.savefig("figs/q1e_scatter.png", dpi=130); plt.close(fig)

# (f) Descriptive statistics -----------------------------------------
desc = pd.DataFrame({
    "mean": lr.mean(), "variance": lr.var(), "std": lr.std(),
    "skewness": lr.apply(stats.skew), "excess kurt": lr.apply(stats.kurtosis),  # Fisher => excess
    "min": lr.min(), "max": lr.max()}).T
print("\n(f) Descriptive statistics (monthly log returns):\n", desc)

# (g) t-test of H0: mean = 0 (two-sided, 5%) --------------------------
print("\n(g) t-tests H0: mean=0")
rows = []
for c in cols:
    t, p = stats.ttest_1samp(lr[c], 0.0)
    rows.append([names[c], lr[c].mean(), t, p, "Reject" if p < .05 else "Do not reject"])
print(pd.DataFrame(rows, columns=["series", "mean", "t", "p-value", "decision @5%"]).to_string(index=False))

# (h) Histograms + fitted normal + Jarque-Bera ------------------------
fig, axs = plt.subplots(2, 3, figsize=(14, 7)); axs = axs.ravel()
for ax, c in zip(axs, cols):
    x = lr[c]; mu, sd = x.mean(), x.std()
    ax.hist(x, bins=40, density=True, alpha=.6)
    g = np.linspace(x.min(), x.max(), 300)
    ax.plot(g, stats.norm.pdf(g, mu, sd), "r", label="Fitted Normal")
    ax.set_title(names[c]); ax.legend()
axs[-1].axis("off")
fig.tight_layout(); fig.savefig("figs/q1h_hist.png", dpi=130); plt.close(fig)
print("\n(h) Jarque-Bera tests (H0: normal)")
rows = []
for c in cols:
    jb, p, s, k = jarque_bera(lr[c])
    rows.append([names[c], jb, p, s, k, "Reject" if p < .05 else "Do not reject"])
print(pd.DataFrame(rows, columns=["series", "JB", "p-value", "skew", "kurtosis(raw)", "decision @5%"]).to_string(index=False))

# (i) CAPM: r_i = alpha + beta * r_VW + e  (rf = 0) -------------------
print("\n(i) CAPM regressions (log returns, rf=0)")
X = sm.add_constant(lr["VWRET"])
for c in ["COCACOLA", "MICROSOFT", "EXXON"]:
    m = sm.OLS(lr[c], X).fit()
    ci = m.conf_int()
    print(f"\n--- {names[c]} ---  R2={m.rsquared:.3f}")
    print(pd.DataFrame({"coef": m.params, "se": m.bse, "t": m.tvalues, "p": m.pvalues,
                        "ci_lo": ci[0], "ci_hi": ci[1]}))
    b = m.params["VWRET"]; se = m.bse["VWRET"]
    print(f"    H0: beta=1  t={(b-1)/se:.3f}, p={2*stats.t.sf(abs((b-1)/se), m.df_resid):.4f}")

# =====================================================================
# QUESTION 2
# =====================================================================
print("\n" + "=" * 70, "\nQUESTION 2\n", "=" * 70)

# (a) Import ----------------------------------------------------------
pen = pd.read_stata("data/pension.dta")
print("(a) shape:", pen.shape)

# (b) Single-person households ----------------------------------------
single = pen[pen["fsize"] == 1].copy()
print(f"(b) single-person households: {len(single)} ({len(single)/len(pen):.2%} of {len(pen)})")

# (c) nettfa = b0 + b1 inc + b2 age + u, singles ----------------------
m1 = smf.ols("nettfa ~ inc + age", data=single).fit()
print("\n(c)\n", m1.summary().tables[1], f"\nR2={m1.rsquared:.4f}, N={int(m1.nobs)}")

# (d) intercept: value at inc=0, age=0 (outside the sample range) -----
print(f"\n(d) intercept={m1.params['Intercept']:.3f}; min age in singles = {single['age'].min()}, min inc = {single['inc'].min():.2f}")

# (e) H0: b2 = 1 vs H1: b2 < 1 ---------------------------------------
b2, se2 = m1.params["age"], m1.bse["age"]
t_e = (b2 - 1) / se2
p_left = stats.t.cdf(t_e, m1.df_resid)
print(f"\n(e) t={t_e:.3f}, one-sided p (left)={p_left:.4f} ->", "reject" if p_left < .05 else "do not reject")

# (f) two-sided -------------------------------------------------------
p_two = 2 * stats.t.sf(abs(t_e), m1.df_resid)
print(f"(f) t={t_e:.3f}, two-sided p={p_two:.4f} ->", "reject" if p_two < .05 else "do not reject")
print("    cross-check with statsmodels t_test:", m1.t_test("age = 1").summary_frame().round(4).to_dict("records"))

# (g) omit age ---------------------------------------------------------
m2 = smf.ols("nettfa ~ inc", data=single).fit()
print(f"\n(g) beta_inc without age = {m2.params['inc']:.4f}  vs with age = {m1.params['inc']:.4f}")
print("    corr(inc, age) in singles =", round(single["inc"].corr(single["age"]), 4))
aux = smf.ols("age ~ inc", data=single).fit()
print("    auxiliary slope delta (age on inc) =", round(aux.params["inc"], 4),
      "-> OVB check: b1 + b2*delta =", round(m1.params["inc"] + m1.params["age"] * aux.params["inc"], 4))

# (h) Full sample, quadratic model ------------------------------------
pen["inc2"] = pen["inc"] ** 2
pen["age2"] = pen["age"] ** 2
f2 = "nettfa ~ inc + age + inc2 + age2 + fsize"
m3 = smf.ols(f2, data=pen).fit()
print("\n(h)\n", m3.summary().tables[1], f"\nR2={m3.rsquared:.4f}, N={int(m3.nobs)}")
b_age, b_age2 = m3.params["age"], m3.params["age2"]
print(f"    d nettfa/d age = {b_age:.3f} + 2*({b_age2:.4f})*age -> positive for age < {-b_age/(2*b_age2):.1f}")
print("    marginal income effect at mean inc:", round(m3.params["inc"] + 2 * m3.params["inc2"] * pen["inc"].mean(), 4))
print("    sample age range:", pen["age"].min(), "-", pen["age"].max())

# (i) F-test H0: b3 = b4 = 0 ------------------------------------------
print("\n(i)", m3.f_test("inc2 = 0, age2 = 0"))

# (j) Rescale inc / 100 (inc2 must be rescaled consistently: (inc/100)^2)
pen["inc_s"] = pen["inc"] / 100
pen["inc_s2"] = pen["inc_s"] ** 2
m4 = smf.ols("nettfa ~ inc_s + age + inc_s2 + age2 + fsize", data=pen).fit()
print("\n(j) rescaled inc (and its square)\n", m4.summary().tables[1])
print("    t(inc) original:", round(m3.tvalues["inc"], 4), "| rescaled:", round(m4.tvalues["inc_s"], 4))
print("    R2 original/rescaled:", round(m3.rsquared, 6), round(m4.rsquared, 6))
# Variant: rescale inc only, keep original inc2 as in the literal wording
m4b = smf.ols("nettfa ~ inc_s + age + inc2 + age2 + fsize", data=pen).fit()
print("    variant (inc2 NOT rescaled): inc_s coef", round(m4b.params["inc_s"], 4), "t", round(m4b.tvalues["inc_s"], 4))

# (k) Robust (White) SEs ----------------------------------------------
m5 = smf.ols(f2, data=pen).fit(cov_type="HC1")
cmp_ = pd.DataFrame({"coef": m3.params, "se_OLS": m3.bse, "t_OLS": m3.tvalues, "p_OLS": m3.pvalues,
                     "se_HC1": m5.bse, "t_HC1": m5.tvalues, "p_HC1": m5.pvalues})
print("\n(k) OLS vs heteroskedasticity-robust (HC1)\n", cmp_)
print("    Breusch-Pagan p:", round(sm.stats.diagnostic.het_breuschpagan(m3.resid, m3.model.exog)[1], 6))

# (l) Standardize all variables of model (1) --------------------------
sz = single[["nettfa", "inc", "age"]]
sz = (sz - sz.mean()) / sz.std()
m6 = smf.ols("nettfa ~ inc + age", data=sz).fit()
print("\n(l) standardized model (1)\n", m6.summary().tables[1])
print("    sd(nettfa), sd(inc), sd(age) in singles:", single[["nettfa", "inc", "age"]].std().round(3).to_dict())
