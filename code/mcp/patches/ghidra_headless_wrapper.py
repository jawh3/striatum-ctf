#!/usr/bin/env python3
"""
Ghidra Headless Analyzer Wrapper for MCP
Provides automated binary analysis without GUI
"""

import subprocess
import json
import os
import tempfile
import shutil
from pathlib import Path

GHIDRA_HOME = os.environ.get("GHIDRA_HOME", "/opt/ghidra")
ANALYZE_HEADLESS = f"{GHIDRA_HOME}/support/analyzeHeadless"
TEMP_PROJECT_DIR = "/tmp/ghidra_headless_projects"


def analyze_binary(binary_path: str, project_name: str = None, 
                   analyze: bool = True, timeout: int = 300) -> dict:
    """
    Analyze a binary using Ghidra headless mode
    
    Args:
        binary_path: Path to the binary to analyze
        project_name: Optional project name (default: uses binary name)
        analyze: Whether to run analysis (default: True)
        timeout: Analysis timeout in seconds (default: 300)
    
    Returns:
        dict with analysis results and project location
    """
    binary_path = Path(binary_path).resolve()
    if not binary_path.exists():
        return {"error": f"Binary not found: {binary_path}"}
    
    # Create temp project directory
    os.makedirs(TEMP_PROJECT_DIR, exist_ok=True)
    
    # Generate project name
    if project_name is None:
        project_name = f"{binary_path.stem}_project"
    
    project_location = Path(TEMP_PROJECT_DIR) / project_name
    
    # Build command
    cmd = [
        ANALYZE_HEADLESS,
        str(TEMP_PROJECT_DIR),
        project_name,
        "-import", str(binary_path),
        "-analysisTimeoutPerFile", str(timeout)
    ]
    
    if not analyze:
        cmd.append("-noanalysis")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 30  # Extra buffer
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "project_location": str(project_location),
            "binary_path": str(binary_path)
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Analysis timeout exceeded",
            "timeout": timeout
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def decompile_function(binary_path: str, function_address: str = None,
                      function_name: str = None) -> dict:
    """
    Decompile a specific function from a binary
    
    Args:
        binary_path: Path to the binary
        function_address: Address of function (e.g., "0x401000")
        function_name: Name of function (e.g., "main")
    
    Returns:
        dict with decompiled code
    """
    # This would require a Ghidra script to extract decompilation
    # For now, we'll create the project and note that GhidraMCP can query it
    
    result = analyze_binary(binary_path)
    
    if result.get("success"):
        return {
            "success": True,
            "message": "Binary analyzed. Use GhidraMCP to query decompiled functions.",
            "project": result["project_location"]
        }
    else:
        return result


def extract_strings(binary_path: str) -> dict:
    """
    Extract strings from a binary using Ghidra
    """
    binary_path = Path(binary_path).resolve()
    
    # Use strings command as quick alternative
    try:
        result = subprocess.run(
            ["strings", str(binary_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        strings_list = result.stdout.strip().split('\n')
        
        return {
            "success": True,
            "strings": strings_list,
            "count": len(strings_list),
            "binary": str(binary_path)
        }
    except Exception as e:
        return {"error": str(e)}


def list_functions(binary_path: str) -> dict:
    """
    List all functions in a binary
    Requires analyzing first, then the result can be queried via GhidraMCP
    """
    result = analyze_binary(binary_path)
    
    if result.get("success"):
        return {
            "success": True,
            "message": "Binary analyzed. Open in Ghidra GUI or use GhidraMCP for function listing.",
            "project": result["project_location"]
        }
    else:
        return result


def cleanup_projects(keep_latest: int = 5):
    """
    Clean up old temporary projects
    
    Args:
        keep_latest: Number of recent projects to keep
    """
    if not os.path.exists(TEMP_PROJECT_DIR):
        return {"message": "No projects to clean"}
    
    projects = sorted(
        Path(TEMP_PROJECT_DIR).iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    removed = []
    for project in projects[keep_latest:]:
        if project.is_dir():
            shutil.rmtree(project)
            removed.append(str(project))
    
    return {
        "cleaned": len(removed),
        "kept": min(len(projects), keep_latest),
        "removed": removed
    }


if __name__ == "__main__":
    # Test the wrapper
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ghidra_headless_wrapper.py <binary_path>")
        sys.exit(1)
    
    binary = sys.argv[1]
    result = analyze_binary(binary)
    print(json.dumps(result, indent=2))
