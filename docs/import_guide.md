# Import Patterns and Troubleshooting Guide

## Common Import Patterns

This guide provides examples of correct import patterns for the IDA Pro MCP project and solutions for common import issues.

### Basic Import Patterns

#### Standard Library Imports

```python
import os
import sys
import json
from typing import Dict, List, Optional, Annotated
```

#### Third-Party Library Imports

```python
from mcp.server.fastmcp import FastMCP
import ida_hexrays
import ida_kernwin
```

#### Project Module Imports

```python
# Absolute imports (preferred for most cases)
from ida_pro_mcp.utils import some_utility_function

# Relative imports (for closely related modules)
from .utils import some_utility_function
```

### Advanced Import Patterns

#### Conditional Imports

Use conditional imports when a module might not be available or when you want to handle import errors gracefully:

```python
try:
    import optional_module
    HAS_OPTIONAL_MODULE = True
except ImportError:
    HAS_OPTIONAL_MODULE = False

def function_that_uses_optional_module():
    if not HAS_OPTIONAL_MODULE:
        return "Optional module not available"
    return optional_module.some_function()
```

#### Lazy Imports

Use lazy imports when you want to defer importing a module until it's actually needed:

```python
def function_that_uses_expensive_module():
    # Import only when the function is called
    import expensive_module
    return expensive_module.some_function()
```

#### Type Checking Imports

Use conditional imports for type checking to avoid runtime dependencies:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeType
```

### Import Aliases

Use import aliases to avoid naming conflicts or to make imports more readable:

```python
import ida_hexrays as hexrays
import ida_kernwin as kernwin
```

## Common Import Issues and Solutions

### Issue: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'ida_pro_mcp'
```

#### Solutions:

1. **Check the Python path**: Ensure the module is in the Python path.

   ```python
   import sys
   print(sys.path)
   ```

2. **Check the package structure**: Ensure the package structure is correct.

   ```
   ida-pro-mcp/
   ├── src/
   │   └── ida_pro_mcp/
   │       ├── __init__.py
   │       └── ...
   ```

3. **Install the package in development mode**: If you're developing the package, install it in development mode.

   ```sh
   pip install -e .
   ```

### Issue: ImportError

```
ImportError: cannot import name 'some_function' from 'ida_pro_mcp.module'
```

#### Solutions:

1. **Check that the name exists**: Ensure the imported name exists in the module.

2. **Check for circular imports**: Ensure there are no circular dependencies.

3. **Check for typos**: Ensure the name is spelled correctly.

### Issue: Circular Imports

Circular imports occur when two modules import each other, directly or indirectly.

#### Solutions:

1. **Import inside functions**: Move imports inside functions where they are needed.

   ```python
   def some_function():
       # Import inside function to avoid circular dependency
       from ida_pro_mcp.another_module import another_function
       return another_function()
   ```

2. **Import at the end of the module**: Place imports at the end of the file.

   ```python
   # At the end of the file
   from ida_pro_mcp.another_module import another_function
   ```

3. **Refactor the code**: Restructure the code to avoid circular dependencies.

   - Move shared functionality to a common module
   - Use dependency injection
   - Use a mediator pattern

### Issue: Relative Import Issues

```
ImportError: attempted relative import beyond top-level package
```

#### Solutions:

1. **Check the package structure**: Ensure the package structure is correct.

2. **Use absolute imports**: Use absolute imports instead of relative imports.

   ```python
   # Instead of
   from ...module import function

   # Use
   from ida_pro_mcp.module import function
   ```

3. **Run the module correctly**: Ensure you're running the module correctly.

   ```sh
   # Instead of
   python module.py

   # Use
   python -m ida_pro_mcp.module
   ```

### Issue: Import Side Effects

Sometimes importing a module can have side effects, such as initializing global variables or running code.

#### Solutions:

1. **Use lazy imports**: Import modules only when needed.

2. **Use conditional imports**: Import modules conditionally.

3. **Refactor the module**: Move initialization code to a function that can be called explicitly.

## Best Practices for Imports

1. **Keep imports at the top of the file**: Place all imports at the top of the file, following the order:
   - Standard library imports
   - Third-party library imports
   - Project module imports

2. **Use absolute imports**: Prefer absolute imports over relative imports, especially for imports across different packages.

3. **Avoid wildcard imports**: Avoid using `from module import *` as it makes it unclear which names are being imported.

4. **Use import aliases**: Use import aliases to avoid naming conflicts or to make imports more readable.

5. **Document dependencies**: Document the dependencies of each module, especially if they are not obvious.

## Tools for Managing Imports

### Static Analysis Tools

- **isort**: Automatically sorts imports according to PEP 8 guidelines.
  ```sh
  pip install isort
  isort your_file.py
  ```

- **pylint**: Checks for import issues and other code quality issues.
  ```sh
  pip install pylint
  pylint your_file.py
  ```

- **mypy**: Checks for type issues, including import issues.
  ```sh
  pip install mypy
  mypy your_file.py
  ```

### Import Visualization

- **pydeps**: Generates a dependency graph for a Python package.
  ```sh
  pip install pydeps
  pydeps your_package
  ```

## Conclusion

Following these import patterns and best practices will help you avoid common import issues and maintain a clean and maintainable codebase. If you encounter import issues, use the solutions provided in this guide to troubleshoot and resolve them.

