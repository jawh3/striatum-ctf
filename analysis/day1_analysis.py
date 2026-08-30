#!/usr/bin/env python3
"""Day-1 zero-compute analyses for the STRIATUM-CTF camera-ready.
Everything is derived from the 180-run outcome table; no new experiments.
Outcome field = duration_min (authoritative; `success` is blank on 24 rows).
"""
import openpyxl, math
import os
from scipy import stats

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ablation_results_documentation.xlsx')
COND = ['Minimal', 'Lessons', 'Templates', 'Baseline']   # ascending doc volume

PUBLIC = {'format string 3', 'angrs 00', 'angrs 01', 'angrs 02',
          'SSTI2', 'Input Injection 1', 'PowerAnalysis Part 2', 'sample3'}
CATEGORY = {
    'sample7': 'M', 'sample3': 'M', 'sample5': 'M', 'format string 3': 'M',
    'sample2': 'R', 'angrs 00': 'R', 'angrs 01': 'R', 'sample6': 'R',
    'sample8': 'W', 'sqli revenge': 'W', 'SSTI2': 'W', 'Input Injection 1': 'W',
    'sample1': 'C', 'angrs 02': 'C', 'PowerAnalysis Part 2': 'C',
}
CATNAME = {'M': 'Memory corruption', 'R': 'Reversing',
           'W': 'Web exploitation', 'C': 'Cryptography'}


def load(rescore_sample7_run2=False):
    wb = openpyxl.load_workbook(XLSX)
    ws = wb['Sheet1']
    runs = []
    for r in ws.iter_rows(min_row=2, max_row=181, max_col=9, values_only=True):
        cid, name, cond, run, dur = r[0], r[1], r[2], r[3], r[4]
        solved = not (isinstance(dur, str) and dur.strip().lower() == 'failed')
        if rescore_sample7_run2 and name == 'sample7' and cond == 'Baseline' and run == 2:
            solved = False
        runs.append(dict(name=name, cond=cond, run=run, solved=solved,
                         dur=dur if solved else None))
    assert len(runs) == 180
    return runs


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def rate(runs, pred):
    sub = [r for r in runs if pred(r)]
    k = sum(r['solved'] for r in sub)
    return k, len(sub)


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{100*k/n:5.1f}% ({k:2d}/{n:2d})  [{lo:4.1f}-{hi:4.1f}]"


def chi2_conditions(runs, label):
    """4x2 chi-square over conditions, run-level."""
    tbl = []
    for c in COND:
        k, n = rate(runs, lambda r, c=c: r['cond'] == c)
        tbl.append([k, n - k])
    chi2, p, dof, _ = stats.chi2_contingency(tbl, correction=False)
    n = sum(sum(row) for row in tbl)
    print(f"  chi2({dof}, N={n}) = {chi2:.2f}, p = {p:.2f}")
    return chi2, p, dof


def section(t):
    print('\n' + '=' * 78 + f"\n{t}\n" + '=' * 78)


def report(runs, tag):
    section(f'[{tag}] 1. FULL SET — sanity check vs Table II')
    for c in COND:
        k, n = rate(runs, lambda r, c=c: r['cond'] == c)
        print(f"  {c:<10} {fmt(k, n)}")
    chi2_conditions(runs, 'full')

    section(f'[{tag}] 2. PROVENANCE SPLIT — public (8) vs non-public (7)')
    pub = [r for r in runs if r['name'] in PUBLIC]
    npu = [r for r in runs if r['name'] not in PUBLIC]
    print(f"  challenges: public={len({r['name'] for r in pub})}  "
          f"non-public={len({r['name'] for r in npu})}")
    for lbl, grp in (('Public (picoCTF+angr)', pub), ('Non-public (archived+internal)', npu)):
        k, n = rate(grp, lambda r: True)
        print(f"\n  {lbl}: aggregate {fmt(k, n)}")
        for c in COND:
            k, n = rate(grp, lambda r, c=c: r['cond'] == c)
            print(f"    {c:<10} {fmt(k, n)}")
    kp, np_ = rate(pub, lambda r: True)
    kn, nn = rate(npu, lambda r: True)
    gap = 100 * (kp / np_ - kn / nn)
    tbl = [[kp, np_ - kp], [kn, nn - kn]]
    chi2, p, dof, _ = stats.chi2_contingency(tbl, correction=False)
    odds, pf = stats.fisher_exact(tbl)
    h = 2 * math.asin(math.sqrt(kp / np_)) - 2 * math.asin(math.sqrt(kn / nn))
    print(f"\n  public - non-public gap = {gap:+.1f} pp")
    print(f"  chi2({dof}, N={np_+nn}) = {chi2:.2f}, p = {p:.2f};  "
          f"Fisher exact p = {pf:.2f};  Cohen's h = {h:+.3f}")
    spread = max(rate(runs, lambda r, c=c: r['cond'] == c)[0] for c in COND) - \
             min(rate(runs, lambda r, c=c: r['cond'] == c)[0] for c in COND)
    print(f"  between-condition spread (full set) = {100*spread/45:.1f} pp  "
          f"-> provenance gap is {'SMALLER' if abs(gap) < 100*spread/45 else 'LARGER'}")

    section(f'[{tag}] 3. SATURATED vs NON-SATURATED CHALLENGES')
    sat, nonsat = [], []
    for name in {r['name'] for r in runs}:
        allruns = [r for r in runs if r['name'] == name]
        (sat if all(r['solved'] for r in allruns) else nonsat).append(name)
    sat, nonsat = sorted(sat), sorted(nonsat)
    print(f"  saturated (12/12): {len(sat)} -> {', '.join(sat)}")
    print(f"  non-saturated:     {len(nonsat)} -> {', '.join(nonsat)}")
    ns = [r for r in runs if r['name'] in nonsat]
    print(f"\n  Per-condition, NON-SATURATED subset only ({len(nonsat)} challenges x 3 runs):")
    for c in COND:
        k, n = rate(ns, lambda r, c=c: r['cond'] == c)
        print(f"    {c:<10} {fmt(k, n)}")
    chi2_conditions(ns, 'subset')
    ka, na = rate(ns, lambda r: r['cond'] == 'Baseline')
    ki, ni = rate(ns, lambda r: r['cond'] == 'Minimal')
    h = 2 * math.asin(math.sqrt(ka / na)) - 2 * math.asin(math.sqrt(ki / ni))
    print(f"  Baseline - Minimal on subset = {100*(ka/na - ki/ni):+.1f} pp,  Cohen's h = {h:+.3f}")
    tot = {c: rate(runs, lambda r, c=c: r['cond'] == c)[0] for c in COND}
    chk = {c: rate(ns, lambda r, c=c: r['cond'] == c)[0] + 3 * len(sat) for c in COND}
    print(f"  cross-check vs Table III column sums: {[tot[c] for c in COND]} "
          f"== {[chk[c] for c in COND]}  -> {'OK' if tot == chk else 'MISMATCH'}")

    section(f'[{tag}] 4. PER-CATEGORY BREAKDOWN')
    print(f"  {'Category':<20}" + ''.join(f"{c:>16}" for c in COND) + f"{'all':>16}")
    for cat in 'MRWC':
        names = {n for n, v in CATEGORY.items() if v == cat}
        row = f"  {CATNAME[cat]+f' ({len(names)})':<20}"
        for c in COND:
            k, n = rate(runs, lambda r, c=c, names=names: r['cond'] == c and r['name'] in names)
            row += f"{100*k/n:>10.1f}% {k:2d}/{n:<2d}"
        k, n = rate(runs, lambda r, names=names: r['name'] in names)
        row += f"{100*k/n:>10.1f}% {k:2d}/{n:<2d}"
        print(row)

    section(f'[{tag}] 5. DURATIONS (successful runs only)')
    for c in COND:
        ds = [r['dur'] for r in runs if r['cond'] == c and r['solved']]
        ds = [float(d) for d in ds]
        capped = [float(r['dur']) if r['solved'] else 60.0
                  for r in runs if r['cond'] == c]
        print(f"  {c:<10} capped-mean {sum(capped)/len(capped):5.2f}  "
              f"success-only mean {sum(ds)/len(ds):5.2f} (n={len(ds)}, "
              f"median {sorted(ds)[len(ds)//2]:.1f})")


runs = load()
report(runs, 'AS-SCORED')

print('\n\n' + '#' * 78)
print('# SENSITIVITY: rescore sample7 / Baseline / run2 as a FAILURE')
print('# (operator note: "had a working exploit at ~19 minutes, but didn\'t let')
print('#  it run long enough. Also ran into a bunch of gdb mcp server issues.")')
print('#' * 78)
report(load(rescore_sample7_run2=True), 'RESCORED')
