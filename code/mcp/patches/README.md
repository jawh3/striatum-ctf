# Local modifications to third-party MCP servers

Kept as descriptions + small files rather than vendored trees, so no third-party
source is redistributed here (clone at the pinned commits via `install_servers.sh`).

## GhidraMCP (LaurieWired) @ 27f316f — Apache-2.0
- `bridge_mcp_ghidra.py`: request timeout raised from 5s to 60s (3 lines) so
  large-binary decompilation does not abort. See `GhidraMCP.timeout.patch`.
- `ghidra_helpers.py`, `ghidra_headless_wrapper.py`: added; hardcoded Ghidra
  install path replaced with the `GHIDRA_HOME` environment variable.
- Change notice per Apache-2.0 §4(b) is recorded in the top-level `NOTICE`.

## secops-mcp (securityfortech) @ 6e09eb7 — MIT
- one-line removal of an unsupported `FastMCP(version=...)` argument. See
  `secops-mcp.version.patch`.

## mcp-gdb (signal-slot) @ edc125d — MIT (declared in package.json; upstream
  ships no LICENSE file). Used unmodified; built with `npm run build`.
