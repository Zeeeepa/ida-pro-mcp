# Developer Guide: Adding New Functionality

## Overview

This guide explains how to add new functionality to the IDA Pro MCP project. The project is designed to make it easy to add new features with minimal boilerplate code.

## Adding New MCP Tools

The IDA Pro MCP project uses a simple architecture that automatically exposes functions in the IDA plugin as MCP tools. To add a new tool:

1. Add a new function to `mcp-plugin.py` with the `@jsonrpc` decorator
2. The function will be automatically available as an MCP tool

### Example: Adding a New Tool

```python
@jsonrpc
@idaread  # Use idaread for read-only operations or idawrite for write operations
def my_new_function(
    param1: Annotated[str, "Description of parameter 1"],
    param2: Annotated[int, "Description of parameter 2"]
) -> dict:
    """Description of what the function does"""
    # Implementation
    result = {"param1": param1, "param2": param2}
    return result
```

### Important Decorators

- `@jsonrpc`: Registers the function as a JSON-RPC method
- `@idaread`: Ensures the function is executed in the main IDA thread (for read operations)
- `@idawrite`: Ensures the function is executed in the main IDA thread (for write operations)
- `@unsafe`: Marks the function as unsafe (will be disabled by default)

### Type Annotations

Use the `Annotated` type from the `typing` module to provide descriptions for parameters:

```python
from typing import Annotated

def my_function(
    param: Annotated[str, "Description of the parameter"]
) -> str:
    """Function description"""
    return param
```

These descriptions will be automatically extracted and included in the MCP tool documentation.

## Testing New Functionality

### Local Testing

1. Install the MCP server and IDA plugin:
   ```sh
   ida-pro-mcp --install
   ```

2. Open IDA Pro and load a binary

3. Start the MCP server in IDA Pro:
   - Click `Edit -> Plugins -> MCP` (or use the hotkey `Ctrl+Alt+M`)

4. Test your new functionality using an MCP client (Cline, Roo Code, Claude, etc.)

### Development Testing

For development and testing without an MCP client:

1. Run the MCP server in development mode:
   ```sh
   uv run mcp dev src/ida_pro_mcp/server.py
   ```

2. This will open a web interface at http://localhost:5173 where you can test your MCP tools

3. Alternatively, you can send JSON-RPC requests directly to the IDA plugin:
   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "my_new_function", "params": ["value1", 42], "id": 1}' http://localhost:13337/mcp
   ```

## Best Practices

### Function Design

1. **Keep functions focused**: Each function should do one thing well
2. **Use descriptive names**: Function names should clearly indicate what they do
3. **Document parameters**: Use `Annotated` to describe parameters
4. **Return meaningful results**: Return structured data that is easy to understand
5. **Handle errors gracefully**: Use `IDAError` for IDA-specific errors

### Thread Safety

IDA Pro is not thread-safe, so all operations that interact with IDA must be executed in the main thread. Use the appropriate decorators:

- `@idaread`: For read-only operations
- `@idawrite`: For operations that modify the database

### Security Considerations

Functions that could potentially be dangerous (e.g., executing arbitrary code) should be marked with the `@unsafe` decorator:

```python
@jsonrpc
@unsafe
def dangerous_function():
    """This function is potentially dangerous"""
    # Implementation
```

Unsafe functions are disabled by default and must be explicitly enabled with the `--unsafe` flag.

## Example: Complete Function Implementation

Here's a complete example of adding a new function to search for bytes in the database:

```python
@jsonrpc
@idaread
def search_bytes(
    pattern: Annotated[str, "Byte pattern to search for (e.g., '41 42 ?? 44')"],
    start_address: Annotated[str, "Start address for the search (hex)"] = "0",
    end_address: Annotated[str, "End address for the search (hex)"] = "0"
) -> list:
    """Search for a byte pattern in the database"""
    # Parse addresses
    start_ea = parse_address(start_address)
    end_ea = parse_address(end_address)
    
    if end_ea == 0:
        end_ea = ida_ida.inf_get_max_ea()
    
    # Parse pattern
    pattern_bytes = []
    for b in pattern.split():
        if b == "??":
            pattern_bytes.append(-1)  # Wildcard
        else:
            pattern_bytes.append(int(b, 16))
    
    # Search for pattern
    results = []
    ea = start_ea
    while ea < end_ea:
        ea = ida_bytes.find_binary(ea, end_ea, bytes(pattern_bytes), 0, ida_bytes.SEARCH_DOWN)
        if ea == ida_idaapi.BADADDR:
            break
        results.append({"address": hex(ea), "name": ida_name.get_name(ea)})
        ea += 1
    
    return results
```

## Updating Documentation

When adding new functionality, make sure to update the relevant documentation:

1. Update the README.md file with a brief description of the new functionality
2. Update this developer guide if necessary
3. Add examples of how to use the new functionality

## Conclusion

Adding new functionality to the IDA Pro MCP project is designed to be simple and straightforward. By following this guide, you can easily extend the project with new features that will be automatically available to MCP clients.

