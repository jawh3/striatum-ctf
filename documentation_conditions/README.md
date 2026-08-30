# Documentation conditions (the ablation's independent variable)

The 180-run study holds the model and tool layer fixed and varies only the
procedural documentation attached to the agent, across four conditions of
increasing size. Those four corpora ARE the independent variable.

| Condition | Lines | Tokens (paper) | Shipped here |
|---|---:|---:|---|
| Minimal (control) | 55 | 591 | **in full** (`minimal/` — tool schemas only) |
| Lessons | 1,478 | 12,865 | manifest only |
| Templates | 1,976 | 17,253 | manifest only |
| Baseline | 4,147 | 36,001 | manifest only |

Under the paper's ethics statement ("no attack-template corpora"), the Lessons,
Templates, and Baseline corpora are **not published**: the Templates/Baseline
solver documentation contains runnable attack payloads. Instead:

- **`manifests/*.manifest.tsv`** give every file's name, line count, and token
  count per condition — these reproduce Table II's Lines/Tokens columns and
  characterize each condition precisely.
- **`template_index.md`** lists the attack-template section headings only (names
  and structure), with all payload bodies removed.

This is a deliberate consequence, noted in the top-level README: the ablation is
not fully reproducible from this repo — only the protocol is. The full solver
protocol is available to researchers for defensive use on request to the
corresponding author.
