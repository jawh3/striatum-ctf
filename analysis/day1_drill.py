#!/usr/bin/env python3
"""Drill-down on the provenance split: is the public/non-public gap evidence of
contamination, or a difficulty confound?"""
import openpyxl, math
import os
from scipy import stats

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ablation_results_documentation.xlsx')
COND = ['Minimal', 'Lessons', 'Templates', 'Baseline']
PICO = {'format string 3', 'SSTI2', 'Input Injection 1', 'PowerAnalysis Part 2', 'sample3'}
ANGR = {'angrs 00', 'angrs 01', 'angrs 02'}
PUBLIC = PICO | ANGR

wb = openpyxl.load_workbook(XLSX); ws = wb['Sheet1']
runs = []
for r in ws.iter_rows(min_row=2, max_row=181, max_col=9, values_only=True):
    dur = r[4]
    runs.append(dict(name=r[1], cond=r[2], run=r[3],
                     solved=not (isinstance(dur, str) and dur.strip().lower() == 'failed'),
                     dur=None if isinstance(dur, str) else dur))

def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n
    c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return 100*(c-h), 100*(c+h)

def cell(sub):
    k, n = sum(x['solved'] for x in sub), len(sub)
    lo, hi = wilson(k, n)
    return f"{100*k/n:5.1f}% ({k:2d}/{n:2d}) [{lo:4.1f}-{hi:4.1f}]", k, n

def compare(a_lbl, a, b_lbl, b):
    sa, ka, na = cell(a); sb, kb, nb = cell(b)
    chi2, p, dof, _ = stats.chi2_contingency([[ka, na-ka], [kb, nb-kb]], correction=False)
    _, pf = stats.fisher_exact([[ka, na-ka], [kb, nb-kb]])
    h = 2*math.asin(math.sqrt(ka/na)) - 2*math.asin(math.sqrt(kb/nb))
    print(f"  {a_lbl:<34} {sa}")
    print(f"  {b_lbl:<34} {sb}")
    print(f"  {'gap':<34} {100*(ka/na-kb/nb):+5.1f} pp   chi2={chi2:.2f} p={p:.3f}  "
          f"Fisher p={pf:.3f}  h={h:+.3f}\n")

print('=' * 78); print('A. PROVENANCE CUTS, all 180 runs'); print('=' * 78)
compare('Public (picoCTF 5 + angr 3)', [r for r in runs if r['name'] in PUBLIC],
        'Non-public (7)', [r for r in runs if r['name'] not in PUBLIC])
compare('picoCTF only (5)', [r for r in runs if r['name'] in PICO],
        'Non-public (7)', [r for r in runs if r['name'] not in PUBLIC])
compare('angr tutorials only (3)', [r for r in runs if r['name'] in ANGR],
        'Everything else (12)', [r for r in runs if r['name'] not in ANGR])

print('=' * 78); print('B. THE CEILING CONFOUND — per-challenge totals (/12), by provenance')
print('=' * 78)
per = {}
for r in runs:
    per.setdefault(r['name'], [0, 0])
    per[r['name']][0] += r['solved']; per[r['name']][1] += 1
for name, (k, n) in sorted(per.items(), key=lambda x: -x[1][0]):
    tag = 'picoCTF' if name in PICO else ('angr' if name in ANGR else 'NON-PUBLIC')
    bar = '#' * k + '.' * (n - k)
    print(f"  {name:<22} {tag:<11} {k:2d}/{n} {bar}")

print('\n' + '=' * 78)
print('C. THE CLEAN TEST — provenance gap WITHIN the non-saturated subset')
print('   (6 challenges, balanced 3 public / 3 non-public — removes the ceiling)')
print('=' * 78)
nonsat = {n for n, (k, t) in per.items() if k < t}
ns = [r for r in runs if r['name'] in nonsat]
print(f"  non-saturated: {sorted(nonsat)}")
print(f"    public     -> {sorted(n for n in nonsat if n in PUBLIC)}")
print(f"    non-public -> {sorted(n for n in nonsat if n not in PUBLIC)}\n")
compare('Public, non-saturated (3)', [r for r in ns if r['name'] in PUBLIC],
        'Non-public, non-saturated (3)', [r for r in ns if r['name'] not in PUBLIC])

print('=' * 78)
print('D. SAME TEST, saturated set only (9 challenges) — sanity: must be 100% vs 100%')
print('=' * 78)
sat = [r for r in runs if r['name'] not in nonsat]
s1, *_ = cell([r for r in sat if r['name'] in PUBLIC])
s2, *_ = cell([r for r in sat if r['name'] not in PUBLIC])
print(f"  public saturated (5)     {s1}")
print(f"  non-public saturated (4) {s2}")
print("\n  -> The entire aggregate provenance gap is carried by which challenges")
print("     happen to sit at the ceiling, not by within-difficulty performance.")

print('\n' + '=' * 78)
print('E. MEDIAN SOLVE TIME (successful runs) by provenance — difficulty proxy')
print('=' * 78)
for lbl, grp in (('picoCTF (5)', PICO), ('angr (3)', ANGR),
                 ('non-public (7)', set(per) - PUBLIC)):
    ds = sorted(float(r['dur']) for r in runs if r['name'] in grp and r['solved'])
    print(f"  {lbl:<16} n={len(ds):3d}  median {ds[len(ds)//2]:5.1f} min  "
          f"mean {sum(ds)/len(ds):5.1f} min  max {ds[-1]:5.1f}")
