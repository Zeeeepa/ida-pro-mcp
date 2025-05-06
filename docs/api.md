# IDA Pro MCP API Reference

This document provides a comprehensive reference for all the API functions available in the IDA Pro MCP server.

## Function Categories

The API functions are organized into the following categories:

1. **Metadata Functions** - Get information about the IDB and current state
2. **Navigation Functions** - Navigate through the IDB
3. **Analysis Functions** - Analyze code and data
4. **Modification Functions** - Modify the IDB
5. **Debugging Functions** - Debug the target program (requires --unsafe flag)

## Metadata Functions

### `check_connection()`
Check if the IDA plugin is running.

**Returns:** A string indicating success or failure

### `get_metadata()`
Get metadata about the current IDB.

**Returns:**
```json
{
  "module": "path/to/binary.exe",
  "input_file_path": "path/to/binary.exe",
  "input_file_md5": "md5hash",
  "processor": "processor_name",
  "compiler": "compiler_name",
  "ida_version": "version_string"
}
```

## Navigation Functions

### `get_function_by_name(name)`
Get a function by its name.

**Parameters:**
- `name` (string): Name of the function to get

**Returns:** Function information object

### `get_function_by_address(address)`
Get a function by its address.

**Parameters:**
- `address` (string): Address of the function (decimal or hexadecimal)

**Returns:** Function information object

### `get_current_address()`
Get the address currently selected by the user.

**Returns:** Current address as a hexadecimal string

### `get_current_function()`
Get the function currently selected by the user.

**Returns:** Function information object or null if no function is selected

## Analysis Functions

### `convert_number(text, size)`
Convert a number (decimal, hexadecimal) to different representations.

**Parameters:**
- `text` (string): Number to convert (decimal, hexadecimal)
- `size` (integer): Size in bytes (1, 2, 4, or 8)

**Returns:** Object with various number representations

### `list_functions(offset, count)`
List all functions in the database (paginated).

**Parameters:**
- `offset` (integer): Starting offset
- `count` (integer): Number of functions to return

**Returns:** Array of function information objects

### `list_strings(offset, count)`
List all strings in the database (paginated).

**Parameters:**
- `offset` (integer): Starting offset
- `count` (integer): Number of strings to return

**Returns:** Array of string information objects

### `search_strings(pattern, offset, count)`
Search for strings containing the given pattern (case-insensitive).

**Parameters:**
- `pattern` (string): Pattern to search for
- `offset` (integer): Starting offset
- `count` (integer): Number of results to return

**Returns:** Array of matching string information objects

### `decompile_function(address)`
Decompile a function at the given address.

**Parameters:**
- `address` (string): Address of the function (decimal or hexadecimal)

**Returns:** Decompiled pseudocode as a string

### `disassemble_function(start_address)`
Get assembly code (address: instruction; comment) for a function.

**Parameters:**
- `start_address` (string): Address of the function (decimal or hexadecimal)

**Returns:** Array of assembly lines with addresses and comments

### `get_xrefs_to(address)`
Get all cross references to the given address.

**Parameters:**
- `address` (string): Target address (decimal or hexadecimal)

**Returns:** Array of cross-reference information objects

### `get_entry_points()`
Get all entry points in the database.

**Returns:** Array of entry point addresses

## Modification Functions

### `set_comment(address, comment)`
Set a comment for a given address in the function disassembly and pseudocode.

**Parameters:**
- `address` (string): Address to comment (decimal or hexadecimal)
- `comment` (string): Comment text

**Returns:** Success indicator

### `rename_local_variable(function_address, old_name, new_name)`
Rename a local variable in a function.

**Parameters:**
- `function_address` (string): Address of the function (decimal or hexadecimal)
- `old_name` (string): Current variable name
- `new_name` (string): New variable name

**Returns:** Success indicator

### `rename_global_variable(old_name, new_name)`
Rename a global variable.

**Parameters:**
- `old_name` (string): Current variable name
- `new_name` (string): New variable name

**Returns:** Success indicator

### `set_global_variable_type(variable_name, new_type)`
Set a global variable's type.

**Parameters:**
- `variable_name` (string): Name of the global variable
- `new_type` (string): New type definition

**Returns:** Success indicator

### `rename_function(function_address, new_name)`
Rename a function.

**Parameters:**
- `function_address` (string): Address of the function (decimal or hexadecimal)
- `new_name` (string): New function name

**Returns:** Success indicator

### `set_function_prototype(function_address, prototype)`
Set a function's prototype.

**Parameters:**
- `function_address` (string): Address of the function (decimal or hexadecimal)
- `prototype` (string): New function prototype

**Returns:** Success indicator

### `declare_c_type(c_declaration)`
Create or update a local type from a C declaration.

**Parameters:**
- `c_declaration` (string): C declaration of the type

**Returns:** Success message with information

### `set_local_variable_type(function_address, variable_name, new_type)`
Set a local variable's type.

**Parameters:**
- `function_address` (string): Address of the function (decimal or hexadecimal)
- `variable_name` (string): Name of the variable
- `new_type` (string): New type for the variable

**Returns:** Success indicator

## Debugging Functions (Unsafe)

These functions require the `--unsafe` flag to be enabled.

### `dbg_get_registers()`
Get all registers and their values. This function is only available when debugging.

**Returns:** Array of register information objects

### `dbg_get_call_stack()`
Get the current call stack.

**Returns:** Array of call stack frame information objects

### `dbg_list_breakpoints()`
List all breakpoints in the program.

**Returns:** Array of breakpoint information objects

### `dbg_start_process()`
Start the debugger.

**Returns:** Success message

### `dbg_exit_process()`
Exit the debugger.

**Returns:** Success message

### `dbg_continue_process()`
Continue the debugger.

**Returns:** Success message

### `dbg_run_to(address)`
Run the debugger to the specified address.

**Parameters:**
- `address` (string): Target address (decimal or hexadecimal)

**Returns:** Success message

### `dbg_set_breakpoint(address)`
Set a breakpoint at the specified address.

**Parameters:**
- `address` (string): Breakpoint address (decimal or hexadecimal)

**Returns:** Success message

### `dbg_delete_breakpoint(address)`
Delete a breakpoint at the specified address.

**Parameters:**
- `address` (string): Breakpoint address (decimal or hexadecimal)

**Returns:** Success message

### `dbg_enable_breakpoint(address, enable)`
Enable or disable a breakpoint at the specified address.

**Parameters:**
- `address` (string): Breakpoint address (decimal or hexadecimal)
- `enable` (boolean): Whether to enable or disable the breakpoint

**Returns:** Success message

