# 14 — angrs_02

| | |
|---|---|
| Category | cryptography |
| Technique | Symbolic execution (condition) |
| Provenance | angr_ctf tutorial 02_angr_find_condition |
| Redistribution | link-only (GPL-3.0) |
| Artifact | fetch from upstream (`../fetch_challenges.sh`) |
| Upstream | https://github.com/jakespringer/angr_ctf |
| SHA-256 (primary artifact) | `ba2ba43e2a9c12bd5d48cb528c198f2b106974a26d7ca76f5c490eb872b0ec31` |
| Note | The study used a locally built binary. Upstream's `dist/` build is a different build and will not match this hash (see `../README.md`). |

## Measured result (successes of 3 per condition)

| Minimal | Lessons | Templates | Baseline |
|:---:|:---:|:---:|:---:|
| 3/3 | 3/3 | 3/3 | 3/3 |

See `../../data/per_challenge_results.csv` (Table III) for the full matrix and
`../../data/ablation_results.csv` for per-run durations. Flags are not included;
verify a fetched artifact against the SHA-256 above where given.
