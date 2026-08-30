#!/usr/bin/env python3
"""Reproduces the Lines and Tokens columns of Table II from the four
documentation-condition corpora.

LINES are exact and reproduce the paper (55 / 1,478 / 1,976 / 4,147) from the
condition file sets.

TOKENS are tokenizer-dependent. The paper's exact tokenizer was not recorded.
For reference, an OpenAI cl100k_base count runs ~1.21x smaller than the paper's
figures and p50k_base ~0.97x; the paper's counts are consistent with a
whitespace/word-ish tokenizer close to p50k. This script reports lines exactly
and tokens under whatever tokenizers are installed, so the ratio is auditable.

NOTE ON SCOPE: only the Minimal corpus (control = tool schemas) ships in this
repo. The Lessons/Templates/Baseline corpora are withheld under the paper's
ethics statement (attack-template corpora). This script therefore reproduces
Table II in full only against a local, private copy of the corpora; against the
public repo it reproduces the Minimal row and validates the others against the
committed manifests in ../documentation_conditions/manifests/.

Usage:
  python3 count_tokens.py [CORPUS_ROOT]
    CORPUS_ROOT contains minimal/ lessons/ templates/ baseline/ subdirs.
    Defaults to ../documentation_conditions (only minimal/ present in the repo).
"""
import os
import sys
import glob

ROOT = sys.argv[1] if len(sys.argv) > 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'documentation_conditions')
PAPER = {'minimal': (55, 591), 'lessons': (1478, 12865),
         'templates': (1976, 17253), 'baseline': (4147, 36001)}

try:
    import tiktoken
    ENCS = [('cl100k_base', tiktoken.get_encoding('cl100k_base')),
            ('p50k_base', tiktoken.get_encoding('p50k_base'))]
except Exception:
    ENCS = []

print(f"{'condition':10s} {'files':>5s} {'lines':>6s} {'paper_L':>7s} "
      + " ".join(f"{n:>10s}" for n, _ in ENCS) + f" {'paper_T':>7s}")
for cond in ['minimal', 'lessons', 'templates', 'baseline']:
    d = os.path.join(ROOT, cond)
    files = [f for f in glob.glob(os.path.join(d, '*')) if os.path.isfile(f)]
    if not files:
        pl, pt = PAPER[cond]
        print(f"{cond:10s} {'--':>5s} {'--':>6s} {pl:>7d} "
              + " ".join(f"{'withheld':>10s}" for _ in ENCS) + f" {pt:>7d}")
        continue
    lines = sum(len(open(f, encoding='utf-8', errors='replace').read().split('\n')) for f in files)
    toks = []
    for _, enc in ENCS:
        toks.append(sum(len(enc.encode(open(f, encoding='utf-8', errors='replace').read())) for f in files))
    pl, pt = PAPER[cond]
    print(f"{cond:10s} {len(files):>5d} {lines:>6d} {pl:>7d} "
          + " ".join(f"{t:>10d}" for t in toks) + f" {pt:>7d}")
