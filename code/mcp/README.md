# The six-server MCP stack

STRIATUM-CTF exposes its tools to the model through six Model Context Protocol
servers, declared in `claude_desktop_config.template.json`:

| Server | Origin | In this repo |
|---|---|---|
| `filesystem` | `@modelcontextprotocol/server-filesystem` (npm) | fetched by npx at run time — **pin an exact version**; the version used in-study was not recorded |
| `angr` | in-house bridge to the angr framework | `angr-bridge/` (MIT) |
| `commands` | in-house command-execution server | `commands-server/` (MIT; original logic by D. Stoller) |
| `gdb` | `signal-slot/mcp-gdb` @ `edc125d` | cloned by `install_servers.sh` |
| `secops` | `securityfortech/secops-mcp` @ `6e09eb7` | cloned by `install_servers.sh` |
| `ghidra` | `LaurieWired/GhidraMCP` @ `27f316f` + local patch | cloned + patched by `install_servers.sh` |

Run `install_servers.sh` with `STRIATUM_ROOT` set; see `patches/` for the exact
third-party modifications. The `secops` server itself downloads the offensive
CLI tools (nmap, nuclei, ffuf, …) at build time — none are redistributed here.

The four Python servers (`angr`, `commands`, `secops`, `ghidra`) run under one
`python3` and all use the 1.x `mcp` API, so install `mcp>=1,<2`: mcp 2.x renamed
`FastMCP` and none of them will start under it. `angr-bridge` also needs
`angr==9.2.176` (see its `pyproject.toml`).
