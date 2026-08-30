#!/usr/bin/env python3
"""
Ensures Ghidra is running and ready for MCP integration.
Called automatically by Claude when Ghidra tools are needed.
"""

import subprocess
import time
import requests
import sys

GHIDRA_MCP_PORT = 8080
GHIDRA_PATH = os.environ.get("GHIDRA_HOME", "/opt/ghidra")

def check_ghidra_running():
    """Check if Ghidra MCP server is responding"""
    try:
        response = requests.get(f"http://localhost:{GHIDRA_MCP_PORT}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ghidra():
    """Launch Ghidra GUI with GhidraMCP plugin enabled"""
    print("[*] Starting Ghidra...")
    
    # Launch Ghidra in background
    subprocess.Popen(
        [f"{GHIDRA_PATH}/ghidraRun"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for Ghidra to start (up to 30 seconds)
    for i in range(30):
        time.sleep(1)
        if check_ghidra_running():
            print("[+] Ghidra is ready!")
            return True
        sys.stdout.write(f"\r[*] Waiting for Ghidra... {i+1}s")
        sys.stdout.flush()
    
    print("\n[!] Ghidra did not start in time. Manual intervention may be needed.")
    return False

def main():
    if check_ghidra_running():
        print("[+] Ghidra is already running and ready!")
        return 0
    
    print("[*] Ghidra not detected. Starting...")
    if start_ghidra():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
