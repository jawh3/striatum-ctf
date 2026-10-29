#!/usr/bin/env python3
"""
Ghidra Helper Functions for Automated Analysis
Works alongside GhidraMCP for binary analysis tasks
"""

import subprocess
import json
import os
from pathlib import Path

GHIDRA_HOME = os.environ.get("GHIDRA_HOME", "/opt/ghidra")


def quick_strings(binary_path: str) -> dict:
    """Extract printable strings from a binary"""
    try:
        result = subprocess.run(
            ["strings", "-n", "4", binary_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        strings_list = [s for s in result.stdout.strip().split('\n') if s]
        return {
            "success": True,
            "strings": strings_list,
            "count": len(strings_list)
        }
    except Exception as e:
        return {"error": str(e)}


def file_info(binary_path: str) -> dict:
    """Get binary file information"""
    try:
        # Run file command
        file_result = subprocess.run(
            ["file", binary_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Run readelf for ELF binaries
        readelf_result = subprocess.run(
            ["readelf", "-h", binary_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return {
            "success": True,
            "file_type": file_result.stdout.strip(),
            "readelf": readelf_result.stdout if readelf_result.returncode == 0 else None
        }
    except Exception as e:
        return {"error": str(e)}


def checksec(binary_path: str) -> dict:
    """Check binary security features"""
    try:
        result = subprocess.run(
            ["checksec", "--file=" + binary_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "success": True,
            "checksec": result.stdout.strip()
        }
    except FileNotFoundError:
        # checksec not installed, use readelf
        try:
            result = subprocess.run(
                ["readelf", "-l", binary_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": True,
                "security_info": "GNU_STACK" in result.stdout,
                "note": "Install checksec for detailed security analysis"
            }
        except Exception as e:
            return {"error": str(e)}


def extract_functions_objdump(binary_path: str) -> dict:
    """Extract function symbols using objdump"""
    try:
        result = subprocess.run(
            ["objdump", "-t", binary_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        functions = []
        for line in result.stdout.split('\n'):
            if 'F .text' in line or 'DF .text' in line:
                parts = line.split()
                if len(parts) >= 2:
                    functions.append({
                        "address": parts[0],
                        "info": ' '.join(parts[1:])
                    })
        
        return {
            "success": True,
            "functions": functions,
            "count": len(functions)
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ghidra_helpers.py <binary>")
        sys.exit(1)
    
    binary = sys.argv[1]
    print("=== File Info ===")
    print(json.dumps(file_info(binary), indent=2))
    print("\n=== Strings (first 20) ===")
    strings_data = quick_strings(binary)
    if strings_data.get("success"):
        for s in strings_data["strings"][:20]:
            print(s)
    print("\n=== Security ===")
    print(json.dumps(checksec(binary), indent=2))
