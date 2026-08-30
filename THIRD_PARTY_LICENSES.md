# Third-party components

None of the following are vendored in this repository; `code/mcp/install_servers.sh`
clones them at the commits below. Listed here for attribution and to record the
terms under which STRIATUM-CTF uses them.

| Component | Upstream | Commit | License | Notes |
|---|---|---|---|---|
| GhidraMCP | github.com/LaurieWired/GhidraMCP | 27f316f | Apache-2.0 | modified — see NOTICE and patches/ |
| secops-mcp | github.com/securityfortech/secops-mcp | 6e09eb7 | MIT | one-line version-arg removal |
| mcp-gdb | github.com/signal-slot/mcp-gdb | edc125d | MIT (declared in package.json; upstream ships no LICENSE file) | used unmodified |
| server-filesystem | @modelcontextprotocol/server-filesystem (npm) | pin at install | Apache-2.0/MIT (in transition) | fetched via npx; pin an exact version |
| angr | github.com/angr/angr | (pkg dep) | BSD-2-Clause | called via public API by the in-house bridge |
| Ghidra | github.com/NationalSecurityAgency/ghidra | — | Apache-2.0 | required at runtime; not bundled |

## Challenge material (not redistributed)
- picoCTF challenges: (c) Carnegie Mellon University, all rights reserved — link only.
- angr_ctf tutorials (github.com/jakespringer/angr_ctf): GPL-3.0 — fetched from upstream.
- System libraries (libc.so.6, ld-linux-*): LGPL-2.1+ — never shipped.
