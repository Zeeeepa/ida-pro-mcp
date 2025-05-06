# IDA Pro MCP

MCP Server for IDA Pro

## Module Structure and Import Conventions

This project follows a standardized module path resolution strategy to ensure consistency and avoid import errors.

### Project Structure

```
ida-pro-mcp/
├── src/
│   └── ida_pro_mcp/
│       ├── __init__.py
│       ├── mcp_plugin.py     # IDA Pro plugin implementation
│       ├── server.py         # MCP server implementation
│       └── idalib_server.py  # IDA library server implementation
├── pyproject.toml            # Project configuration
└── ida-plugin.json           # IDA plugin configuration
```

### Import Conventions

1. **Absolute Imports**

   Always use absolute imports from the package root:

   ```python
   # Good
   from ida_pro_mcp import mcp_plugin
   
   # Avoid
   from .mcp_plugin import something
   ```

2. **External Dependencies**

   External dependencies should be imported directly:

   ```python
   # Good
   from mcp.server.fastmcp import FastMCP
   
   # Avoid
   import mcp
   ```

3. **Module Naming**

   All module names should follow Python conventions:
   - Use lowercase
   - Use underscores instead of hyphens
   - Be descriptive and clear

### Development Guidelines

1. **Adding New Modules**

   When adding new modules, follow these steps:
   - Place the module in the `src/ida_pro_mcp/` directory
   - Use a descriptive name with underscores
   - Update `__init__.py` if necessary to expose public interfaces

2. **Importing Between Modules**

   When importing between modules in this package:
   - Use absolute imports from the package root
   - Import only what you need, not entire modules

## Installation

```bash
pip install ida-pro-mcp
```

## Usage

See the documentation for usage instructions.

