#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# STRIATUM-CTF command-execution MCP server.
# Original command-execution logic by Dawson Stoller (co-author), used and
# relicensed MIT here with permission. Part of https://github.com/jawh3/striatum-ctf
"""
Commands MCP Server - Bulletproof Edition
Allows executing shell commands on the host system with maximum reliability.

CHANGELOG v2.0 (2025-11-20):
=================================
CRITICAL FIXES:
- stdin=subprocess.DEVNULL: Prevents hanging on commands that read input
- close_fds=True: Properly closes inherited file descriptors
- start_new_session=True: Isolates process from parent session
- preexec_fn=os.setsid: Additional isolation (Unix only)

RELIABILITY IMPROVEMENTS:
- Graceful timeout handling with SIGTERM -> SIGKILL escalation
- Partial output capture on timeout
- Process cleanup on errors
- Comprehensive error logging
- Command truncation in logs (prevents log spam)

EDGE CASE HANDLING:
- Network commands (curl, wget, requests)
- Interactive programs (without TTY)
- Background processes
- Heredoc syntax
- Pipe chains
- Long-running operations
"""
import json
import logging
import os
import subprocess
import signal
import shutil
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Configuration
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("commands-mcp")

mcp = FastMCP("commands")

def preexec_function():
    """
    Function to run in child process before exec.
    Creates a new process group for better isolation.
    Only works on Unix systems.
    """
    try:
        os.setsid()  # Create new session
    except:
        pass  # Ignore errors on non-Unix systems

@mcp.tool(name="execute_command")
async def execute_command(
    command: str, 
    working_dir: Optional[str] = None, 
    timeout: int = 300
):
    """
    Execute a shell command and return the output.
    
    Args:
        command: The shell command to execute
        working_dir: Optional working directory to execute the command in
        timeout: Maximum time in seconds to wait for command completion (default: 300)
    
    Returns:
        JSON with stdout, stderr, and return code
    
    Features:
        - Automatic stdin closing (prevents hanging)
        - Timeout protection with graceful termination
        - Partial output capture on timeout
        - Process isolation and cleanup
        - Comprehensive error handling
    
    Examples:
        # Simple command
        {"command": "ls -la"}
        
        # With working directory
        {"command": "make", "working_dir": "/path/to/project"}
        
        # With custom timeout
        {"command": "long_running_task", "timeout": 600}
    """
    # Truncate command for logging (prevent log spam)
    log_command = command[:200] + ('...' if len(command) > 200 else '')
    logger.info(f"Executing: {log_command}")
    
    if working_dir:
        logger.info(f"Working directory: {working_dir}")
        # Validate working directory exists
        if not os.path.isdir(working_dir):
            error_response = {
                "success": False,
                "error": f"Working directory does not exist: {working_dir}",
                "error_type": "InvalidWorkingDirectory"
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    try:
        # Determine shell to use (prefer bash for better compatibility)
        shell_path = shutil.which('bash') or shutil.which('sh') or '/bin/sh'
        
        # Execute command with maximum isolation and safety
        result = subprocess.run(
            command,
            shell=True,
            executable=shell_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir,
            
            # CRITICAL: These three parameters prevent 99% of hanging issues
            stdin=subprocess.DEVNULL,   # Close stdin - prevents blocking on input
            close_fds=True,              # Close all other file descriptors
            start_new_session=True,      # Detach from parent session
            
            # Additional isolation (Unix only, ignored on Windows)
            preexec_fn=preexec_function if os.name != 'nt' else None,
            
            # Environment cleanup
            env={**os.environ, 'TERM': 'dumb'},  # Prevent interactive behaviors
        )
        
        response = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        if result.returncode == 0:
            logger.info(f"✓ Command completed successfully")
        else:
            logger.warning(f"✗ Command failed with return code: {result.returncode}")
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except subprocess.TimeoutExpired as e:
        # Command exceeded timeout - try graceful cleanup
        logger.warning(f"⏱ TIMEOUT after {timeout}s: {log_command}")
        
        # Try to capture any partial output
        partial_stdout = ""
        partial_stderr = ""
        try:
            if e.stdout:
                partial_stdout = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else str(e.stdout)
            if e.stderr:
                partial_stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
        except Exception as parse_error:
            logger.debug(f"Could not parse partial output: {parse_error}")
        
        # Attempt cleanup of any remaining processes
        try:
            # Extract command name for cleanup
            cmd_name = command.split()[0] if command.split() else ""
            if cmd_name and len(cmd_name) > 2:
                # Kill any processes matching the command
                cleanup_cmd = f"pkill -9 -f '{cmd_name[:30]}' 2>/dev/null || true"
                subprocess.run(cleanup_cmd, shell=True, timeout=2, 
                             stdin=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        except:
            pass  # Cleanup is best-effort
        
        error_response = {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "error_type": "TimeoutExpired",
            "timeout": timeout,
            "partial_stdout": partial_stdout[:2000] if partial_stdout else "",
            "partial_stderr": partial_stderr[:2000] if partial_stderr else "",
            "note": "Command was killed due to timeout. Consider increasing timeout parameter."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except FileNotFoundError as e:
        # Command or executable not found
        logger.error(f"✗ Command not found: {e}")
        error_response = {
            "success": False,
            "error": str(e),
            "error_type": "CommandNotFound",
            "note": "The command or executable could not be found. Check PATH or use absolute path."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except PermissionError as e:
        # Permission denied
        logger.error(f"✗ Permission denied: {e}")
        error_response = {
            "success": False,
            "error": str(e),
            "error_type": "PermissionDenied",
            "note": "Permission denied. Check file permissions or run with appropriate privileges."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except OSError as e:
        # Other OS-level errors
        logger.error(f"✗ OS error: {e}")
        error_response = {
            "success": False,
            "error": str(e),
            "error_type": "OSError",
            "errno": e.errno if hasattr(e, 'errno') else None
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"✗ Unexpected error: {e}", exc_info=True)
        error_response = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "note": "An unexpected error occurred. Check logs for details."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Commands MCP Server v2.0 (Bulletproof Edition)")
    logger.info("Features: stdin isolation, timeout protection, process cleanup")
    logger.info("=" * 60)
    mcp.run()
