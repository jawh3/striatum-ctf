# Analysis

Reproduces every statistic in the paper from `../data/`. `pip install -r requirements.txt` first.

| Script | Reproduces |
|---|---|
| `day1_analysis.py` | Table II success rates + 95% Wilson CIs; the 4×2 omnibus chi-square (chi2(3,N=180)=1.36, p=0.71); the non-saturated 6-challenge subset (44.4/55.6/61.1/66.7%, chi2(3,N=72)=1.98, p=0.58); Cohen's h; per-category breakdown; durations both ways. Includes the sample7-run2 rescoring sensitivity pass. |
| `day1_drill.py` | Provenance drill-down: public (picoCTF+angr) vs non-public success, with chi-square / Fisher / Cohen's h. (Reported in neither table — supporting analysis.) |
| `duration_and_gee.py` | Kruskal-Wallis on durations (p=0.77) and the logistic GEE with challenge-level clustering (Wald chi2(3)=3.77, p=0.29). |
| `count_tokens.py` | Table II line counts (exact) and token counts. Only the Minimal corpus ships; the other three are validated against `../documentation_conditions/manifests/`. |

Outcome coding throughout: a run is solved iff `duration_min` is numeric. See `../data/codebook.md`.
