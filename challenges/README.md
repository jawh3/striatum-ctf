# Challenges

The 15-challenge benchmark. **No challenge binaries are mirrored here** where we
lack redistribution rights; `manifest.csv` records provenance, redistribution
status, upstream URL, and a SHA-256 of the primary artifact so a fetched copy can
be verified.

- **`manifest.csv`** — the 15 challenges, one row each.
- **`fetch_challenges.sh`** — clones the GPL-3.0 angr_ctf tutorials from upstream
  and prints instructions for obtaining the 5 picoCTF challenges (CMU,
  all-rights-reserved — not mirrorable).
- **`cards/`** — one spec card per challenge: category, technique, provenance,
  and the measured per-condition result. These fully characterize the benchmark
  even where the artifact itself cannot be shipped.
- **`sources/`** — the two challenge sources we may redistribute (author
  permission): `sqli_revenge` (SQLi+WAF, by A. Leach) and `sample1` (weak RSA).

Flags are not included. Six FSU/custom challenges (sample2/5/6/7/8, and the
sqli/sample1 binaries) are course material without a public license; they are
described in `cards/` only.

## Verifying against `manifest.csv`

Each hash is of the file a solver receives: the binary, the `.jar`, `traces.zip`,
or the challenge source. Two exceptions:

- **angrs_00/01/02.** The study used locally built binaries of these three
  angr_ctf levels. The prebuilt binaries in upstream's `dist/` are different
  builds, so a copy fetched by `fetch_challenges.sh` will not match the
  manifest. The hash identifies the instance the study ran on. (The paper's
  footnote for these points to `angr/angr-doc`; the challenges themselves come
  from `jakespringer/angr_ctf`.)
- **SSTI2** has no hash. It is a live web instance with no downloadable file.
