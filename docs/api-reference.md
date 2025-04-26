# API Reference

This document provides detailed information about all the functions available in the IDA Pro MCP API.

## Core Functions

### check_connection

```
check_connection()
```

Check if the IDA plugin is running.

**Returns**: A string indicating whether the connection to IDA Pro was successful.

### get_metadata

```
get_metadata()
```

Get metadata about the current IDB.

**Returns**: An object containing metadata about the currently loaded binary, including:
- `module`: The name of the loaded binary
- `path`: The full path to the binary
- `architecture`: The architecture of the binary
- `compiler`: The compiler used to build the binary
- `base_address`: The base address of the binary
- `entry_point`: The entry point of the binary

## Navigation Functions

### get_current_address

```
get_current_address()
```

Get the address currently selected by the user.

**Returns**: The current address as a string in hexadecimal format.

### get_current_function

```
get_current_function()
```

Get the function currently selected by the user.

**Returns**: An object containing information about the current function, or null if no function is selected.

### get_function_by_name

```
get_function_by_name(name)
```

Get a function by its name.

**Parameters**:
- `name` (string): Name of the function to get

**Returns**: An object containing information about the function, or null if the function is not found.

### get_function_by_address

```
get_function_by_address(address)
```

Get a function by its address.

**Parameters**:
- `address` (string): Address of the function to get (in hexadecimal format)

**Returns**: An object containing information about the function, or null if no function exists at the specified address.

## Analysis Functions

### list_functions

```
list_functions(offset, count)
```

List all functions in the database (paginated).

**Parameters**:
- `offset` (number): Starting index for pagination
- `count` (number): Number of functions to return

**Returns**: An array of function objects.

### list_strings

```
list_strings(offset, count)
```

List all strings in the database (paginated).

**Parameters**:
- `offset` (number): Starting index for pagination
- `count` (number): Number of strings to return

**Returns**: An array of string objects, each containing the address and value of the string.

### search_strings

```
search_strings(pattern, offset, count)
```

Search for strings containing the given pattern (case-insensitive).

**Parameters**:
- `pattern` (string): Pattern to search for
- `offset` (number): Starting index for pagination
- `count` (number): Number of results to return

**Returns**: An array of string objects that match the pattern.

### decompile_function

```
decompile_function(address)
```

Decompile a function at the given address.

**Parameters**:
- `address` (string): Address of the function to decompile (in hexadecimal format)

**Returns**: The decompiled pseudocode of the function.

### disassemble_function

```
disassemble_function(start_address)
```

Get assembly code (address: instruction; comment) for a function.

**Parameters**:
- `start_address` (string): Address of the function to disassemble (in hexadecimal format)

**Returns**: The disassembled code of the function.

### get_xrefs_to

```
get_xrefs_to(address)
```

Get all cross references to the given address.

**Parameters**:
- `address` (string): Address to get cross references to (in hexadecimal format)

**Returns**: An array of cross reference objects.

### get_entry_points

```
get_entry_points()
```

Get all entry points in the database.

**Returns**: An array of entry point objects.

### convert_number

```
convert_number(text, size)
```

Convert a number (decimal, hexadecimal) to different representations.

**Parameters**:
- `text` (string): The number to convert (e.g., "42", "0x2A")
- `size` (number, optional): The size of the number in bits (8, 16, 32, 64)

**Returns**: An object containing different representations of the number.

## Modification Functions

### set_comment

```
set_comment(address, comment)
```

Set a comment for a given address in the function disassembly and pseudocode.

**Parameters**:
- `address` (string): Address to set the comment for (in hexadecimal format)
- `comment` (string): The comment text

**Returns**: A success message if the comment was set successfully.

### rename_local_variable

```
rename_local_variable(function_address, old_name, new_name)
```

Rename a local variable in a function.

**Parameters**:
- `function_address` (string): Address of the function containing the variable (in hexadecimal format)
- `old_name` (string): Current name of the variable
- `new_name` (string): New name for the variable

**Returns**: A success message if the variable was renamed successfully.

### rename_global_variable

```
rename_global_variable(old_name, new_name)
```

Rename a global variable.

**Parameters**:
- `old_name` (string): Current name of the variable
- `new_name` (string): New name for the variable

**Returns**: A success message if the variable was renamed successfully.

### set_global_variable_type

```
set_global_variable_type(variable_name, new_type)
```

Set a global variable's type.

**Parameters**:
- `variable_name` (string): Name of the variable
- `new_type` (string): New type for the variable (e.g., "int", "char*")

**Returns**: A success message if the type was set successfully.

### rename_function

```
rename_function(function_address, new_name)
```

Rename a function.

**Parameters**:
- `function_address` (string): Address of the function to rename (in hexadecimal format)
- `new_name` (string): New name for the function

**Returns**: A success message if the function was renamed successfully.

### set_function_prototype

```
set_function_prototype(function_address, prototype)
```

Set a function's prototype.

**Parameters**:
- `function_address` (string): Address of the function (in hexadecimal format)
- `prototype` (string): New prototype for the function (e.g., "int foo(int a, char* b)")

**Returns**: A success message if the prototype was set successfully.

### declare_c_type

```
declare_c_type(c_declaration)
```

Create or update a local type from a C declaration.

**Parameters**:
- `c_declaration` (string): C declaration of the type (e.g., "typedef int foo_t;", "struct bar { int a; bool b; };")

**Returns**: A success message if the type was declared successfully.

### set_local_variable_type

```
set_local_variable_type(function_address, variable_name, new_type)
```

Set a local variable's type.

**Parameters**:
- `function_address` (string): Address of the function containing the variable (in hexadecimal format)
- `variable_name` (string): Name of the variable
- `new_type` (string): New type for the variable (e.g., "int", "char*")

**Returns**: A success message if the type was set successfully.

## Debugging Functions

These functions are marked as unsafe and are only available when the `--unsafe` flag is used.

### dbg_get_registers

```
dbg_get_registers()
```

Get all registers and their values. This function is only available when debugging.

**Returns**: An array of register objects.

### dbg_get_call_stack

```
dbg_get_call_stack()
```

Get the current call stack.

**Returns**: An array of call stack frame objects.

### dbg_list_breakpoints

```
dbg_list_breakpoints()
```

List all breakpoints in the program.

**Returns**: An array of breakpoint objects.

### dbg_start_process

```
dbg_start_process()
```

Start the debugger.

**Returns**: A success message if the debugger was started successfully.

### dbg_exit_process

```
dbg_exit_process()
```

Exit the debugger.

**Returns**: A success message if the debugger was exited successfully.

### dbg_continue_process

```
dbg_continue_process()
```

Continue the debugger.

**Returns**: A success message if the debugger was continued successfully.

### dbg_run_to

```
dbg_run_to(address)
```

Run the debugger to the specified address.

**Parameters**:
- `address` (string): Address to run to (in hexadecimal format)

**Returns**: A success message if the debugger was run to the specified address successfully.

### dbg_set_breakpoint

```
dbg_set_breakpoint(address)
```

Set a breakpoint at the specified address.

**Parameters**:
- `address` (string): Address to set the breakpoint at (in hexadecimal format)

**Returns**: A success message if the breakpoint was set successfully.

### dbg_delete_breakpoint

```
dbg_delete_breakpoint(address)
```

Delete a breakpoint at the specified address.

**Parameters**:
- `address` (string): Address to delete the breakpoint from (in hexadecimal format)

**Returns**: A success message if the breakpoint was deleted successfully.

### dbg_enable_breakpoint

```
dbg_enable_breakpoint(address, enable)
```

Enable or disable a breakpoint at the specified address.

**Parameters**:
- `address` (string): Address of the breakpoint (in hexadecimal format)
- `enable` (boolean): Whether to enable or disable the breakpoint

**Returns**: A success message if the breakpoint was enabled/disabled successfully.
