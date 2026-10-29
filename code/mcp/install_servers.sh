#!/usr/bin/env bash
# Assemble the six-server MCP stack used by STRIATUM-CTF.
# Two servers (angr-bridge, commands-server) ship in this repo; three are
# third-party and are cloned at the exact commits used in the study, then
# patched; one (filesystem) is fetched from npm at run time.
#
# Usage:  STRIATUM_ROOT=/path/to/install  ./install_servers.sh
set -euo pipefail
: "${STRIATUM_ROOT:?set STRIATUM_ROOT to the install directory}"
SRV="$STRIATUM_ROOT/servers"; mkdir -p "$SRV" "$STRIATUM_ROOT/workspace"   # workspace = the filesystem server's root
HERE="$(cd "$(dirname "$0")" && pwd)"

clone() { # url  dir  commit
  if [ ! -d "$SRV/$2" ]; then git clone "$1" "$SRV/$2"; fi
  git -C "$SRV/$2" checkout -q -f "$3"   # -f resets earlier patches so a re-run applies cleanly
}

# --- third-party servers, pinned to study commits ---
clone https://github.com/LaurieWired/GhidraMCP        GhidraMCP  27f316f
clone https://github.com/securityfortech/secops-mcp   secops-mcp 6e09eb7
clone https://github.com/signal-slot/mcp-gdb          mcp-gdb    edc125d
# upstream has no lockfile at edc125d; the study's lockfile pins the exact dependency versions
cp "$HERE/patches/mcp-gdb.package-lock.json" "$SRV/mcp-gdb/package-lock.json"
( cd "$SRV/mcp-gdb" && npm ci && npm run build )   # produces build/index.js

# --- apply the local modifications documented in patches/ ---
cp "$HERE/patches/ghidra_helpers.py" "$HERE/patches/ghidra_headless_wrapper.py" "$SRV/GhidraMCP/"
git -C "$SRV/GhidraMCP"  apply "$HERE/patches/GhidraMCP.timeout.patch"
git -C "$SRV/secops-mcp" apply "$HERE/patches/secops-mcp.version.patch"

# --- in-house servers ship in this repo, installed under the names the host config uses ---
mkdir -p "$SRV/angr" "$SRV/mcp-server-commands"
cp -r "$HERE/angr-bridge/."     "$SRV/angr/"
cp -r "$HERE/commands-server/." "$SRV/mcp-server-commands/"

echo "Done. Now point Claude Desktop at claude_desktop_config.template.json"
echo "with STRIATUM_ROOT expanded, and start a Ghidra headless server on :8080."
