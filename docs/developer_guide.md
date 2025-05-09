# IDA Pro MCP Developer Guide

This guide provides information for developers who want to extend or modify the IDA Pro MCP project.

## Development Environment Setup

1. **Prerequisites**
   - Python 3.11 or higher
   - IDA Pro 8.3 or higher (9 recommended)
   - Git

2. **Clone the Repository**
   ```sh
   git clone https://github.com/mrexodia/ida-pro-mcp.git
   cd ida-pro-mcp
   ```

3. **Install Development Dependencies**
   ```sh
   pip install --upgrade uv
   uv pip install -e ".[dev]"
   ```

## Project Structure

```
ida-pro-mcp/
├── docs/                    # Documentation
├── src/                     # Source code
│   └── ida_pro_mcp/         # Main package
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation
│       ├── mcp-plugin.py    # IDA Pro plugin
│       └── idalib_server.py # Headless server implementation
├── pyproject.toml           # Project metadata and dependencies
├── LICENSE                  # License information
└── README.md                # Project overview
```

## Adding New Functions

Adding new functionality to the IDA Pro MCP server is straightforward:

1. **Add a New Function to mcp-plugin.py**

   ```python
   @jsonrpc
   @idaread  # or @idawrite if the function modifies the database
   def my_new_function(
       param1: Annotated[str, "Description of param1"],
       param2: Annotated[int, "Description of param2"]
   ) -> dict:
       """Description of what the function does"""
       # Implementation
       result = {}
       # ... your code here ...
       return result
   ```

2. **For Potentially Dangerous Functions, Add the @unsafe Decorator**

   ```python
   @jsonrpc
   @idaread
   @unsafe
   def my_unsafe_function():
       """Description of what the function does"""
       # Implementation
       # ...
   ```

3. **No Additional Configuration Needed**

   The function will be automatically discovered and made available through the MCP server.

## Thread Synchronization

IDA Pro is not thread-safe, so all operations that interact with IDA must be properly synchronized:

- Use the `@idaread` decorator for functions that read from the IDA database
- Use the `@idawrite` decorator for functions that modify the IDA database

These decorators ensure that the operations are executed in the main IDA thread.

## Testing

To test the MCP server:

1. **Start the Development Server**
   ```sh
   uv run mcp dev src/ida_pro_mcp/server.py
   ```

2. **Open the Web Interface**
   Navigate to http://localhost:5173 to interact with the MCP tools for testing.

3. **Test with IDA Pro**
   - Install the plugin: `uv run ida-pro-mcp --install`
   - Open IDA Pro and load a binary
   - Start the plugin from Edit -> Plugins -> MCP (Ctrl+Alt+M)
   - Test your functions through the web interface or an MCP client

## Debugging

For debugging the MCP server:

1. **Enable Verbose Logging**
   ```sh
   uv run mcp dev src/ida_pro_mcp/server.py --transport http://127.0.0.1:8744
   ```

2. **Use the MCP Inspector**
   ```sh
   npx @modelcontextprotocol/inspector
   ```
   Connect to http://127.0.0.1:8744/sse to inspect the MCP communication.

3. **Direct JSON-RPC Testing**
   You can send JSON-RPC requests directly to the IDA plugin at http://localhost:13337/mcp:
   ```sh
   curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"get_metadata","params":[],"id":1}' http://localhost:13337/mcp
   ```

## Building and Distribution

To build the package for distribution:

1. **Update Version**
   Update the version in `pyproject.toml`.

2. **Build the Package**
   ```sh
   python -m build
   ```

3. **Test the Package**
   ```sh
   pip install dist/ida_pro_mcp-x.y.z-py3-none-any.whl
   ```

## Best Practices

1. **Documentation**
   - Use descriptive docstrings for all functions
   - Use `Annotated[type, "description"]` for parameter documentation
   - Keep the README.md updated with new functionality

2. **Error Handling**
   - Use the `IDAError` class for IDA-specific errors
   - Provide clear error messages that help users understand what went wrong

3. **Security**
   - Mark potentially dangerous functions with the `@unsafe` decorator
   - Validate all input parameters before using them

4. **Performance**
   - Minimize the number of IDA API calls, especially in loops
   - Use pagination for functions that return large amounts of data

5. **Compatibility**
   - Test with different versions of IDA Pro
   - Handle differences in IDA API versions gracefully

