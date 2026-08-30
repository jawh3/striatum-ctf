# Minimal CTF Solver Guide

## Available MCP Servers

You have access to these tool servers:

### GDB (Dynamic Debugging)
- `gdb:gdb_start()` - Start GDB session
- `gdb:gdb_load()` - Load binary
- `gdb:gdb_command()` - Execute GDB command
- `gdb:gdb_set_breakpoint()` - Set breakpoint
- `gdb:gdb_continue()` - Continue execution
- `gdb:gdb_examine()` - Examine memory
- `gdb:gdb_print()` - Print expression
- `gdb:gdb_backtrace()` - Show stack trace

### Ghidra (Static Analysis)
- `ghidra:list_functions()` - List all functions
- `ghidra:decompile_function()` - Decompile function to C
- `ghidra:list_strings()` - List strings in binary
- `ghidra:get_xrefs_to()` - Get cross-references
- `ghidra:rename_function()` - Rename function

### angr (Symbolic Execution)
- `angr:solve_by_address()` - Solve by reaching target address
- `angr:solve_by_output()` - Solve by matching output string

### SecOps (Web/Network Tools)
- `secops:nmap_wrapper()` - Port scanning
- `secops:sqlmap_wrapper()` - SQL injection testing
- `secops:nuclei_scan_wrapper()` - Vulnerability scanning
- `secops:ffuf_wrapper()` - Fuzzing
- `secops:xsstrike_wrapper()` - XSS testing

### Filesystem Operations
- `filesystem:read_text_file()` - Read file
- `filesystem:write_file()` - Write file
- `filesystem:list_directory()` - List directory

### Commands (Shell Execution)
- `commands:execute_command()` - Execute shell command

## Critical Notes

- **Use `commands:execute_command` for running binaries** (NOT bash_tool)
- Challenges are in: `${STRIATUM_ROOT}/challenges/`
- Your workspace is in: `${STRIATUM_ROOT}/workspaces/`

## General Approach

1. Analyze the challenge (file type, strings, behavior)
2. Identify vulnerability type
3. Use appropriate tools to exploit
4. Retrieve the flag
