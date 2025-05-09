# Module Import Guidelines

This document provides guidelines for adding new modules to the ida-pro-mcp project to ensure proper import resolution and prevent runtime errors.

## Module Structure

The ida-pro-mcp project follows a standard Python package structure:

```
ida-pro-mcp/
├── src/
│   └── ida_pro_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── idalib_server.py
│       └── mcp-plugin.py
├── tests/
│   ├── test_imports.py
│   └── test_static_imports.py
└── pyproject.toml
```

## Adding New Modules

When adding new modules to the project, follow these guidelines:

1. **Place modules in the correct location**:
   - All modules should be placed in the `src/ida_pro_mcp/` directory
   - Use appropriate subdirectories for logical organization

2. **Update `__init__.py`**:
   - If you want a module to be part of the public API, import it in `__init__.py`
   - Example: `from .my_module import MyClass, my_function`

3. **Use relative imports**:
   - When importing from within the package, use relative imports
   - Example: `from . import server` or `from .utils import helper_function`

4. **Avoid circular imports**:
   - Be careful not to create circular import dependencies
   - If necessary, use deferred imports inside functions

5. **Document dependencies**:
   - If your module requires external dependencies, add them to `pyproject.toml`

## Testing Module Imports

Before submitting changes, run the import tests to ensure all modules can be imported correctly:

```bash
# Run the basic import tests
python tests/test_imports.py

# Run the static analysis tests
python tests/test_static_imports.py

# Or run all tests using pytest
pytest
```

## Common Import Issues and Solutions

### 1. ModuleNotFoundError

This occurs when Python cannot find the module you're trying to import.

**Solutions**:
- Check the module path and ensure it's in the correct location
- Verify the spelling of the import statement
- Make sure the package is installed if it's an external dependency

### 2. ImportError

This occurs when the module is found but cannot be loaded due to an error.

**Solutions**:
- Check for syntax errors in the imported module
- Ensure all dependencies of the imported module are available
- Look for circular import issues

### 3. Circular Imports

This happens when module A imports module B, and module B imports module A.

**Solutions**:
- Restructure your code to avoid the circular dependency
- Move the import statement inside the function that needs it
- Create a third module that both modules can import

### 4. Relative Import Issues

These occur when relative imports are used incorrectly.

**Solutions**:
- Use the correct number of dots in relative imports
- Ensure the module is being run as part of a package
- Use absolute imports for clarity when appropriate

## Best Practices

1. **Keep modules focused**: Each module should have a single responsibility
2. **Minimize dependencies**: Only import what you need
3. **Use explicit imports**: Avoid `from module import *`
4. **Test imports**: Run the import tests after adding new modules
5. **Document public API**: Clearly document which modules and functions are part of the public API

