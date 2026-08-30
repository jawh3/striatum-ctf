#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Part of STRIATUM-CTF (https://github.com/jawh3/striatum-ctf). MIT-licensed.
# Uses the angr binary-analysis framework (BSD-2-Clause) via its public API.
"""
angr FastMCP Bridge – **minimalist edition**
==========================================
Two tools, implemented independently against angr's public Python API

* **solve_by_address(path, good_addr, bad_addr)**
* **solve_by_output(path, success_text, fail_text)**

No registry, no custom stdin, no extras – the bridge invokes angr's public
Project/simulation-manager API and returns the satisfying input.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _Timeout
from pathlib import Path
from typing import Optional

import angr  # type: ignore
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("angr‑mcp‑barebones")

POOL = ThreadPoolExecutor(max_workers=4)
mcp = FastMCP("angr barebones bridge")

# --------------------------------------------------------------------------

def _solve_by_address(path: str, good: int, bad: Optional[int], max_steps: int):
    import sys
    project = angr.Project(path)
    state = project.factory.entry_state(
        add_options={angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                     angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS})
    simgr = project.factory.simgr(state)
    simgr.explore(find=good, avoid=bad, n=max_steps)
    if simgr.found:
        st = simgr.found[0]
        password = st.posix.dumps(sys.stdin.fileno()).decode(errors="ignore")
        return {"ok": True, "password": password.strip()}
    return {"ok": False}


def _solve_by_output(path: str, success: bytes, fail: Optional[bytes], max_steps: int):
    import sys
    project = angr.Project(path)
    state = project.factory.entry_state(
        add_options={angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                     angr.options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS})
    simgr = project.factory.simgr(state)

    def is_successful(s):
        return success in s.posix.dumps(sys.stdout.fileno())

    def should_abort(s):
        return fail is not None and fail in s.posix.dumps(sys.stdout.fileno())

    simgr.explore(find=is_successful, avoid=should_abort, n=max_steps)
    if simgr.found:
        st = simgr.found[0]
        password = st.posix.dumps(sys.stdin.fileno()).decode(errors="ignore")
        return {"ok": True, "password": password.strip()}
    return {"ok": False}

# ---------------------------------------------------------------- tools ----
@mcp.tool(name="solve_by_address")
async def solve_by_address(path: str, good_addr: str, bad_addr: str = "", max_steps: int = 100000,
                           timeout: int = 300):
    """Solve via addresses. `good_addr`/`bad_addr` are hex strings like "0x80492fb"."""
    try:
        if not Path(path).exists():
            return [TextContent(type="text", text=json.dumps({"error": "file not found"}))]
        good = int(good_addr, 16)
        bad = int(bad_addr, 16) if bad_addr else None
        fut = POOL.submit(_solve_by_address, path, good, bad, max_steps)
        res = fut.result(timeout=timeout)
        return [TextContent(type="text", text=json.dumps(res))]
    except _Timeout:
        return [TextContent(type="text", text=json.dumps({"error": "timeout"}))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

@mcp.tool(name="solve_by_output")
async def solve_by_output(path: str, success_text: str = "Good Job.", fail_text: str = "Try again.",
                          max_steps: int = 100000, timeout: int = 300):
    """Solve via printed strings. Text matches are case‑sensitive substrings."""
    try:
        if not Path(path).exists():
            return [TextContent(type="text", text=json.dumps({"error": "file not found"}))]
        fut = POOL.submit(_solve_by_output, path, success_text.encode(),
                          fail_text.encode() if fail_text else None, max_steps)
        res = fut.result(timeout=timeout)
        return [TextContent(type="text", text=json.dumps(res))]
    except _Timeout:
        return [TextContent(type="text", text=json.dumps({"error": "timeout"}))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

# --------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("angr barebones bridge listening on 127.0.0.1:7782 …")
    mcp.run()
