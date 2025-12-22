# Development Guide

This guide is intended for developers who want to contribute to IDA Pro MCP or extend its functionality.

## Setting Up the Development Environment

1. Clone the repository:
   ```sh
   git clone https://github.com/mrexodia/ida-pro-mcp.git
   cd ida-pro-mcp
   ```

2. Install the development dependencies:
   ```sh
   pip install uv
   uv pip install -e ".[dev]"
   ```

3. Install the plugin for testing:
   ```sh
   uv run ida-pro-mcp --install
   ```

## Project Structure

The project is organized as follows:

- `src/ida_pro_mcp/`: Main package directory
  - `__init__.py`: Package initialization
  - `server.py`: MCP server implementation
  - `mcp-plugin.py`: IDA Pro plugin implementation
  - `idalib_server.py`: Alternative server using idalib
- `docs/`: Documentation
- `pyproject.toml`: Project configuration
- `LICENSE`: License information
- `README.md`: Project overview

## Adding New Functions

Adding new functions to IDA Pro MCP is straightforward. Here's how to add a new function:

1. Open `src/ida_pro_mcp/mcp-plugin.py`
2. Add a new function with the `@jsonrpc` decorator:

```python
@jsonrpc
@idaread  # or @idawrite if the function modifies the database
def my_new_function(
    param1: Annotated[str, "Description of param1"],
    param2: Annotated[int, "Description of param2"]
) -> dict:
    """Description of what the function does"""
    # Implementation
    return {"result": "success"}
```

3. Restart the MCP server and IDA Pro plugin

That's it! The function will be automatically available through the MCP server.

### Function Decorators

- `@jsonrpc`: Registers the function as a JSON-RPC method
- `@idaread`: Ensures the function is executed in the IDA Pro thread (for read operations)
- `@idawrite`: Ensures the function is executed in the IDA Pro thread (for write operations)
- `@unsafe`: Marks the function as unsafe (only available with the `--unsafe` flag)

### Parameter Annotations

Use `Annotated[type, "description"]` to provide descriptions for parameters. These descriptions will be automatically included in the MCP tool documentation.

## Testing

To test the MCP server:

```sh
uv run mcp dev src/ida_pro_mcp/server.py
```

This will open a web interface at http://localhost:5173 and allow you to interact with the MCP tools for testing.

For testing with IDA Pro, you can create a symbolic link to the IDA plugin and then POST a JSON-RPC request directly to `http://localhost:13337/mcp`.

## Debugging

For debugging the MCP server, you can use the `--verbose` flag:

```sh
ida-pro-mcp --verbose
```

For debugging the IDA Pro plugin, you can add print statements that will appear in the IDA Pro output window.

## Building and Packaging

The project uses setuptools for building and packaging. To build the package:

```sh
pip install build
python -m build
```

This will create a wheel file in the `dist/` directory that can be installed with pip.

## Release Process

To release a new version:

1. Update the version number in `pyproject.toml`
2. Update the changelog in `README.md`
3. Commit the changes
4. Create a new tag with the version number
5. Push the tag to GitHub
6. Create a new release on GitHub

## Code Style

The project follows PEP 8 for code style. Some key points:

- Use 4 spaces for indentation
- Use snake_case for function and variable names
- Use CamelCase for class names
- Add docstrings to all functions and classes
- Keep lines under 100 characters

## Documentation

Documentation is written in Markdown and stored in the `docs/` directory. To update the documentation:

1. Edit the relevant Markdown files
2. Commit the changes
3. Push to GitHub

## Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request

Please follow the existing code style and add appropriate documentation for your changes.

## License

IDA Pro MCP is licensed under the MIT License. See the `LICENSE` file for details.
