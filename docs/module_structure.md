# Module Structure and Import Conventions

## Overview

This document outlines the module structure and import conventions for the IDA Pro MCP project. Following these guidelines will help prevent import errors and improve developer onboarding.

## Module Structure

The IDA Pro MCP application is organized into the following modules:

### Core Modules

- **ida_pro_mcp**: Main package containing all functionality
  - **__init__.py**: Package initialization
  - **server.py**: Main MCP server implementation for communicating with LLM clients
  - **idalib_server.py**: Server implementation for direct IDA library integration
  - **mcp-plugin.py**: IDA Pro plugin that provides JSON-RPC interface

### Module Dependencies

```
ida_pro_mcp
├── server.py
│   └── Dependencies:
│       ├── mcp.server.fastmcp (FastMCP)
│       └── Standard libraries (os, sys, ast, json, shutil, argparse, http.client, urllib.parse)
│
├── idalib_server.py
│   └── Dependencies:
│       ├── mcp.server.fastmcp (FastMCP)
│       ├── idapro
│       ├── ida_auto, ida_hexrays
│       └── Standard libraries (sys, inspect, logging, argparse, importlib, pathlib)
│
└── mcp-plugin.py
    └── Dependencies:
        ├── IDA SDK modules (ida_hexrays, ida_kernwin, ida_funcs, etc.)
        └── Standard libraries (os, sys, re, json, struct, threading, http.server, urllib.parse)
```

### Directory Structure

```
ida-pro-mcp/
├── .github/                  # GitHub configuration files
├── docs/                     # Documentation files
│   └── module_structure.md   # This document
├── src/                      # Source code
│   └── ida_pro_mcp/          # Main package
│       ├── __init__.py       # Package initialization
│       ├── server.py         # MCP server implementation
│       ├── idalib_server.py  # IDA library server
│       └── mcp-plugin.py     # IDA Pro plugin
├── .gitignore                # Git ignore file
├── .python-version           # Python version specification
├── LICENSE                   # License file
├── README.md                 # Project readme
├── ida-plugin.json           # Plugin configuration
├── pyproject.toml            # Project configuration
├── uv-package.sh             # UV packaging script
└── uv.lock                   # UV lock file
```

## Import Conventions

When importing modules in the IDA Pro MCP project, follow these conventions:

### 1. Standard Library Imports

Standard library imports should be grouped at the top of the file, sorted alphabetically:

```python
import os
import sys
import json
import argparse
```

### 2. Third-Party Library Imports

Third-party library imports should be placed after standard library imports, with a blank line separating them:

```python
import os
import sys

from mcp.server.fastmcp import FastMCP
```

### 3. Project Module Imports

Project-specific imports should be placed after third-party imports, with a blank line separating them:

```python
import os
import sys

from mcp.server.fastmcp import FastMCP

from ida_pro_mcp.utils import some_utility_function
```

### 4. IDA SDK Imports

IDA SDK imports should be grouped together, after other imports:

```python
import os
import sys

from mcp.server.fastmcp import FastMCP

import ida_hexrays
import ida_kernwin
import ida_funcs
import idaapi
```

### 5. Relative vs. Absolute Imports

- **Use relative imports** for importing modules within the same package:

```python
# Good - importing from the same package
from .utils import some_utility_function
```

- **Use absolute imports** for importing modules from different packages:

```python
# Good - importing from a different package
from ida_pro_mcp.utils import some_utility_function
```

### 6. Avoid Deep Relative Paths

```python
# Bad - too many levels of relativity
from ....ida_pro_mcp.utils import some_utility_function

# Good - use absolute imports instead
from ida_pro_mcp.utils import some_utility_function
```

### 7. Import Aliases

Use import aliases when importing modules with long names or to avoid naming conflicts:

```python
# Good - using an alias for clarity
import ida_hexrays as hexrays
```

### 8. Handling Circular Dependencies

Circular dependencies should be avoided whenever possible. If unavoidable, use one of these approaches:

1. **Import inside functions**: Move imports inside functions where they are needed

```python
def some_function():
    # Import inside function to avoid circular dependency
    from ida_pro_mcp.another_module import another_function
    return another_function()
```

2. **Import at the end of the module**: Place imports at the end of the file

```python
# At the end of the file
from ida_pro_mcp.another_module import another_function
```

## Adding New Modules

When adding a new module to the IDA Pro MCP project:

1. **Place it in the appropriate directory** based on its functionality
2. **Follow the import conventions** outlined above
3. **Update the `__init__.py`** file if necessary to expose public functions/classes
4. **Add unit tests** for the new module
5. **Update this documentation** if the module structure changes significantly

### Example: Adding a New Utility Module

```python
# src/ida_pro_mcp/utils.py

"""
Utility functions for the IDA Pro MCP project.
"""

import os
import sys

def some_utility_function():
    """
    A utility function that does something useful.
    """
    return "Something useful"
```

Then, in `__init__.py`:

```python
# src/ida_pro_mcp/__init__.py

from .utils import some_utility_function

__all__ = ["some_utility_function"]
```

## Testing Module Imports

To ensure that your imports are working correctly, you can use the following approaches:

1. **Run the application**: The most straightforward way to test imports is to run the application and check for import errors.

2. **Use unit tests**: Write unit tests that import your modules to ensure they can be imported correctly.

3. **Use static analysis tools**: Tools like `pylint` or `mypy` can help identify import issues.

## Troubleshooting Import Issues

Common import issues and their solutions:

1. **ModuleNotFoundError**: Ensure the module is in the Python path and that the package structure is correct.

2. **ImportError**: Check that the imported name exists in the module and that there are no circular dependencies.

3. **Circular imports**: Refactor the code to avoid circular dependencies, or use one of the approaches mentioned above.

4. **Relative import issues**: Ensure that relative imports are used correctly and that the package structure is properly defined.

## Best Practices

1. **Keep modules focused**: Each module should have a single responsibility.

2. **Minimize dependencies**: Avoid unnecessary dependencies between modules.

3. **Document public interfaces**: Clearly document the public interface of each module.

4. **Use type hints**: Use type hints to make the code more readable and maintainable.

5. **Follow PEP 8**: Follow the PEP 8 style guide for Python code.

## Conclusion

Following these module structure and import conventions will help maintain a clean and maintainable codebase. It will also make it easier for new developers to understand and contribute to the project.

