#!/usr/bin/env python3
"""Reproduces the two inferential statistics reported in the paper that the
Day-1 scripts do not compute:

  * Kruskal--Wallis on run durations           -> p = 0.77   (Section V-C)
  * Logistic GEE, challenge-level clustering    -> Wald chi2(3) = 3.77, p = 0.29

Outcome coding matches the paper: a run is solved iff `duration_min` is numeric
("Failed" = unsolved). Timed-out runs are imputed at the 60-minute cap for the
duration test, which is the convention Table II's caption states.

Requires: pandas, scipy, statsmodels, openpyxl  (see requirements.txt)
"""
import os
import numpy as np
import openpyxl
from scipy import stats
import statsmodels.api as sm
import statsmodels.genmod.generalized_estimating_equations as gee

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', 'data', 'ablation_results_documentation.xlsx')
COND = ['Minimal', 'Lessons', 'Templates', 'Baseline']
CAP = 60.0

wb = openpyxl.load_workbook(XLSX)
rows = [r for r in wb['Sheet1'].iter_rows(min_row=2, max_row=181, max_col=9, values_only=True)]

dur, solved, cond_idx, challenge = [], [], [], []
for r in rows:
    cid, c, d = r[0], r[2], r[4]
    is_fail = isinstance(d, str) and d.strip().lower() == 'failed'
    solved.append(0 if is_fail else 1)
    dur.append(CAP if is_fail else float(d))
    cond_idx.append(COND.index(c))
    challenge.append(cid)
dur = np.array(dur); solved = np.array(solved)
cond_idx = np.array(cond_idx); challenge = np.array(challenge)

# ---- Kruskal-Wallis on durations (timed-out runs at the 60-min cap) ----
groups = [dur[cond_idx == k] for k in range(4)]
H, p_kw = stats.kruskal(*groups)
print("Kruskal-Wallis on run durations (timed-out at 60-min cap)")
print(f"  H = {H:.3f}, p = {p_kw:.2f}   (paper: p = 0.77)")
print(f"  per-condition mean minutes: " +
      ", ".join(f"{c}={g.mean():.1f}" for c, g in zip(COND, groups)))

# ---- Logistic GEE, exchangeable, clustered on challenge ----
# design matrix: intercept + 3 dummies (Minimal = reference)
X = np.zeros((180, 3))
for i, k in enumerate(cond_idx):
    if k > 0:
        X[i, k - 1] = 1
X = sm.add_constant(X)
model = gee.GEE(solved, X, groups=challenge,
                family=sm.families.Binomial(),
                cov_struct=sm.cov_struct.Exchangeable()).fit()
wald = model.wald_test(np.eye(4)[1:], scalar=True)
print("\nLogistic GEE, exchangeable working correlation, clustered on challenge")
print(f"  joint condition effect: Wald chi2(3) = {float(wald.statistic):.2f}, "
      f"p = {float(wald.pvalue):.2f}   (paper: 3.77, 0.29)")
