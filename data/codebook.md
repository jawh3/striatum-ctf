# Data codebook

## `ablation_results.csv` — the 180-run outcome table

180 rows = 15 challenges × 4 documentation conditions × 3 runs. Columns:

| Column | Meaning |
|---|---|
| `challenge_id` | 1–15 |
| `challenge_name` | challenge identifier (spaced form, e.g. `angrs 00`) |
| `documentation_condition` | Minimal, Lessons, Templates, or Baseline |
| `run_number` | 1–3 |
| `duration_min` | wall-clock minutes to solve, **or the literal string `Failed`** for an unsolved run |
| `success` | `yes` / blank (see rule below) |
| `approach_taken`, `notes`, `date` | free-text operator fields; mostly empty |

### Two scoring rules you must apply to reproduce the paper

1. **`duration_min` is authoritative, not `success`.** The `success` column is
   blank on 24 of 180 rows; `duration_min` is populated on all 180. A run counts
   as **solved iff `duration_min` is numeric** (`Failed` = unsolved). Using the
   `success` column instead will miscount.

2. **One internally inconsistent cell is scored as a failure.** Row
   `sample2 / Lessons / run 2` has `duration_min = Failed` but `success = yes`.
   It is counted as a **failure**, which yields Lessons = 37/45 and matches both
   the paper and the published companion study. `analysis/day1_analysis.py`
   includes a sensitivity pass that also re-scores `sample7 / Baseline / run 2`
   (the note "had a working exploit at ~19 min but didn't let it run long
   enough") to show the ordering's dependence on that judgment.

Durations are reported two ways in the paper: mean over all 45 runs with
timed-out runs imputed at the 60-minute cap (Table II "Time" column, tracks
success rate), and mean over successful runs only (§IV-C, where Minimal is
fastest). Both are computed in the analysis scripts.

## `per_challenge_results.csv`
The 15×4 successes-out-of-3 matrix (Table III), with a TOTAL row (35/37/38/39).
Derived from `ablation_results.csv` by counting non-`Failed` runs per cell.

## `live_ctf_progression.csv`
Cumulative solves over time for the top-10 teams in the live competition
(Fig. 2), columns `team, minutes_since_0900, cumulative_solves`. **Reverse-
engineered from the published figure's vector content**, not measured directly;
each curve's vertex count equals its final solve count. The competition **point
totals (215 / 205 / 200) are not in any released artifact** — the scoreboard
export was not retained — so this file carries solves, not points.

Five teams' last solves fall between 241 and 254 minutes, past the event's
scheduled four hours. This is consistent with the scoreboard staying open
briefly past the scheduled close; the exact closing time was not recorded, and
the times are as recovered from the figure.
