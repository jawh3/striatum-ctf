# STRIATUM-CTF

Artifacts for **"STRIATUM-CTF: A Protocol-Driven Agentic Framework for Autonomous
CTF Solving"** (IEEE CARS 2026), Hugglestone, Chacko, Stoller, Schmidt, and Liu,
Florida State University.

This repository supports replication of the **protocol and the analysis**. It is
not a turnkey exploit kit: per the paper's ethics statement, no exploit payloads
or attack-template corpora are released. What that means concretely is spelled
out under [Scope and exclusions](#scope-and-exclusions) below.

## What's here

| Directory | Contents |
|---|---|
| `data/` | The 180-run outcome table (`ablation_results.csv` + source `.xlsx`), the per-challenge matrix (Table III), the live-CTF solve progression (Fig. 2), rendered figures, and a `codebook.md`. |
| `analysis/` | Scripts that reproduce every statistic in the paper from `data/`. |
| `code/` | The six-server MCP stack: two in-house servers, an installer that pins the three third-party servers to their study commits, and the host config. |
| `challenges/` | Provenance manifest with verification hashes, a fetch script for the redistributable challenges, per-challenge spec cards, and the two challenge sources we may redistribute. |
| `documentation_conditions/` | The four ablation conditions: the Minimal corpus in full, per-condition file/line/token manifests (which reproduce Table II), and a headings-only template index. |

## Reproducing the paper's numbers

```bash
cd analysis
pip install -r requirements.txt
python3 day1_analysis.py      # Tables II & III, Wilson CIs, chi-square, subset analysis, durations
python3 day1_drill.py         # provenance drill-down (public vs non-public)
python3 duration_and_gee.py   # Kruskal-Wallis (p=0.77) and the GEE model (Wald chi2(3)=3.77, p=0.29)
python3 count_tokens.py       # Table II line counts (exact) and token counts
```

All of Tables II and III, the 95% Wilson intervals, the omnibus tests, the
non-saturated subset analysis, the GEE model, and the duration figures reproduce
exactly from `data/`. Table II's **line** counts reproduce exactly; the **token**
counts are tokenizer-dependent and the paper's exact tokenizer was not recorded
(see `analysis/count_tokens.py` and the per-condition manifests).

## Scope and exclusions

Two independent reasons limit what ships. Neither is an oversight.

**Ethics (paper §"Ethical Considerations"): no exploit payloads or attack-template
corpora.** Therefore withheld:
- the ~1,800 files under the original `workspaces/` tree (working exploits, solver
  scripts, and solution write-ups) — the per-run *outcomes* are released as
  `data/ablation_results.csv` instead;
- the Templates and Baseline solver corpora (`AUTONOMOUS_SOLVER_README.md`,
  `TEMPLATE_COVERAGE.md`), which are the attack templates the ethics statement
  names. These are *characterized* — file lists, line and token counts, and a
  headings-only index in `documentation_conditions/` — so the ablation's
  independent variable is documented, but the payloads are not published;
- all recovered flags (verify fetched artifacts against the SHA-256 values in
  `challenges/manifest.csv` instead).

**Consequence, stated plainly:** because the Templates/Baseline corpora are the
manipulation in the 180-run study, that ablation is **not fully reproducible from
this repository** — only the *protocol* is. The full solver protocol is available
to researchers for defensive use on request to the corresponding author.

**Licensing:** challenge binaries are not mirrored where we lack the right to
redistribute them — picoCTF challenges (CMU, all rights reserved) and the angr_ctf
tutorials (GPL-3.0) are fetched from upstream by `challenges/fetch_challenges.sh`;
system libraries (`libc`, `ld-linux`) are never shipped. See `THIRD_PARTY_LICENSES.md`.

## Two things that cannot be reproduced, by construction

- **The exact per-run numbers cannot be re-executed.** The backbone (Claude
  Sonnet 4.5, via the Claude Desktop for Linux host) is no longer served. The
  artifacts here support replicating the protocol on a *current* backbone, as the
  paper's Threats to Validity states.
- **Per-call tool-execution logs were never retained** (the desktop host does not
  persist per-call MCP traces, and no logging proxy was interposed). The paper's
  Future Work describes the stdio proxy that would capture them.

## Citing

See `CITATION.cff`. Paper: IEEE Cyber Awareness and Research Symposium (CARS) 2026.

## License

Authors' own code and documentation: MIT (`LICENSE`). Third-party components
retain their own licenses; see `NOTICE` and `THIRD_PARTY_LICENSES.md`.
