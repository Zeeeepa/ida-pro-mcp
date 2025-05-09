# IDA Pro MCP Documentation

## Overview

This directory contains comprehensive documentation for the IDA Pro MCP project, focusing on module structure, import conventions, and developer guidelines.

## Documentation Files

- [Module Structure and Import Conventions](module_structure.md): Comprehensive documentation of the application's module structure and import conventions.
- [Module Hierarchy](module_hierarchy.md): Visual representation of the module hierarchy and dependencies.
- [Developer Guide](developer_guide.md): Guide for adding new modules and functionality to the application.
- [Import Guide](import_guide.md): Detailed guide on import patterns and troubleshooting common import issues.

## Quick Reference

### Module Structure

The IDA Pro MCP application is organized into the following modules:

- **ida_pro_mcp**: Main package containing all functionality
  - **server.py**: Main MCP server implementation
  - **idalib_server.py**: Server implementation for direct IDA library integration
  - **mcp-plugin.py**: IDA Pro plugin that provides JSON-RPC interface

### Import Conventions

When importing modules, follow these conventions:

1. **Use relative imports** for modules within the same package:
   ```python
   # Good - importing from the same package
   from .utils import some_utility_function
   ```

2. **Use absolute imports** for modules from different packages:
   ```python
   # Good - importing from a different package
   from ida_pro_mcp.utils import some_utility_function
   ```

3. **Avoid deep relative paths**:
   ```python
   # Bad - too many levels of relativity
   from ....ida_pro_mcp.utils import some_utility_function
   
   # Good - use absolute imports instead
   from ida_pro_mcp.utils import some_utility_function
   ```

### Adding New Modules

When adding a new module:

1. Place it in the appropriate directory based on its functionality
2. Follow the import conventions outlined in the documentation
3. Update the `__init__.py` file if necessary to expose public functions/classes
4. Add unit tests for the module
5. Update the documentation if the module structure changes significantly

## Contributing to Documentation

If you find any issues or have suggestions for improving this documentation, please open an issue or submit a pull request. We welcome contributions that make the documentation more clear, comprehensive, and useful.

