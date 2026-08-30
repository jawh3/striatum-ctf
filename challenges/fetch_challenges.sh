#!/usr/bin/env bash
# Fetch the redistributable challenges from their rightful sources.
# picoCTF challenges (CMU, all rights reserved) are NOT mirrored here — play/
# download them from picoCTF; angr_ctf challenges are GPL-3.0 and are cloned
# from upstream. FSU/custom challenges are not publicly redistributable and are
# described by spec cards only (see cards/).
#
# After fetching, verify against manifest.csv's SHA-256 column where present.
set -euo pipefail
DEST="${1:-./fetched}"; mkdir -p "$DEST"

echo "[angr_ctf] cloning GPL-3.0 tutorial challenges (angrs_00/01/02)…"
if [ ! -d "$DEST/angr_ctf" ]; then
  git clone https://github.com/jakespringer/angr_ctf "$DEST/angr_ctf"
fi
echo "  angrs_00 -> $DEST/angr_ctf (00_angr_find)"
echo "  angrs_01 -> $DEST/angr_ctf (01_angr_avoid)"
echo "  angrs_02 -> $DEST/angr_ctf (02_angr_find_condition)"

cat <<'NOTE'

[picoCTF] The 5 picoCTF challenges are all-rights-reserved (CMU) and cannot be
mirrored. Obtain them from https://play.picoctf.org :
  sample3           = picoMini (redpwn) "clutter-overflow"
  format_string_3   = "format-string-3"
  SSTI2             = picoCTF 2025 "SSTI2"
  Input_Injection_1 = picoMini
  PowerAnalysis_Part_2 = picoCTF 2023 (Power Analysis, Part 2)

[FSU/custom] sample1, sample2, sample5, sample6, sample7, sample8 are course
material without a public license. sample1 (weak-RSA source) and sqli_revenge
(app source) are included in ../sources/ with the authors' permission; the
others are described in cards/ only.
NOTE
echo "Done. Verify fetched artifacts against manifest.csv SHA-256 values."
