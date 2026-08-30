#!/usr/bin/env bash
# Assemble the six-server MCP stack used by STRIATUM-CTF.
# Two servers (angr-bridge, commands-server) ship in this repo; three are
# third-party and are cloned at the exact commits used in the study, then
# patched; one (filesystem) is fetched from npm at run time.
#
# Usage:  STRIATUM_ROOT=/path/to/install  ./install_servers.sh
set -euo pipefail
: "${STRIATUM_ROOT:?set STRIATUM_ROOT to the install directory}"
SRV="$STRIATUM_ROOT/servers"; mkdir -p "$SRV"; HERE="$(cd "$(dirname "$0")" && pwd)"

clone() { # url  dir  commit
  if [ ! -d "$SRV/$2" ]; then git clone "$1" "$SRV/$2"; fi
  git -C "$SRV/$2" checkout "$3"
}

# --- third-party servers, pinned to study commits ---
clone https://github.com/LaurieWired/GhidraMCP        GhidraMCP  27f316f
clone https://github.com/securityfortech/secops-mcp   secops-mcp 6e09eb7
clone https://github.com/signal-slot/mcp-gdb          mcp-gdb    edc125d
( cd "$SRV/mcp-gdb" && npm ci && npm run build )   # produces build/index.js

# --- apply the local modifications documented in patches/ ---
cp "$HERE/patches/ghidra_helpers.py"        "$SRV/GhidraMCP/ghidra_helpers.py"        2>/dev/null || true
cp "$HERE/patches/ghidra_headless_wrapper.py" "$SRV/GhidraMCP/ghidra_headless_wrapper.py" 2>/dev/null || true
git -C "$SRV/GhidraMCP" apply "$HERE/patches/GhidraMCP.timeout.patch" 2>/dev/null || \
  echo "  (apply GhidraMCP.timeout.patch by hand if it does not apply to your checkout)"

# --- in-house servers ship in this repo ---
cp -r "$HERE/angr-bridge"     "$SRV/angr-bridge"
cp -r "$HERE/../mcp/commands-server" "$SRV/commands-server"

echo "Done. Now point Claude Desktop at claude_desktop_config.template.json"
echo "with STRIATUM_ROOT expanded, and start a Ghidra headless server on :8080."
