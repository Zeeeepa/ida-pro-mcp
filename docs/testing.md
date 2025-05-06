# IDA Pro MCP Testing Guide

This document outlines the testing process for the IDA Pro MCP project, including manual testing procedures and results.

## Testing Environment

### Recommended Testing Setup

- **Operating Systems**:
  - Windows 10/11
  - macOS (latest version)
  - Linux (Ubuntu 20.04 or newer)

- **IDA Pro Versions**:
  - IDA Pro 8.3
  - IDA Pro 9.0 (recommended)

- **Python Versions**:
  - Python 3.11
  - Python 3.12

- **MCP Clients**:
  - Claude Desktop
  - Cline
  - Roo Code
  - Cursor
  - VSCode Agent Mode

## Testing Procedures

### 1. Installation Testing

1. **Fresh Installation**
   - Install the package: `pip install --upgrade git+https://github.com/mrexodia/ida-pro-mcp`
   - Configure MCP servers: `ida-pro-mcp --install`
   - Verify that the plugin is installed in the IDA plugins directory
   - Verify that the MCP server configuration is updated for all supported clients

2. **Upgrade Testing**
   - Install an older version
   - Upgrade to the latest version
   - Verify that the upgrade process completes without errors
   - Verify that the plugin and configuration are updated correctly

3. **Uninstallation Testing**
   - Run `ida-pro-mcp --uninstall`
   - Verify that the plugin is removed from the IDA plugins directory
   - Verify that the MCP server configuration is updated to remove the server

### 2. Functionality Testing

1. **Connection Testing**
   - Start IDA Pro and load a binary
   - Start the MCP plugin (Edit -> Plugins -> MCP)
   - Connect with an MCP client
   - Verify that the `check_connection` tool returns success

2. **Metadata Functions**
   - Test `get_metadata()`
   - Verify that the returned information matches the loaded binary

3. **Navigation Functions**
   - Test `get_function_by_name()` with various function names
   - Test `get_function_by_address()` with various addresses
   - Test `get_current_address()` and `get_current_function()`
   - Verify that the returned information is accurate

4. **Analysis Functions**
   - Test `convert_number()` with various inputs
   - Test `list_functions()` and `list_strings()` with pagination
   - Test `search_strings()` with various patterns
   - Test `decompile_function()` and `disassemble_function()`
   - Test `get_xrefs_to()` and `get_entry_points()`
   - Verify that the returned information is accurate

5. **Modification Functions**
   - Test `set_comment()` with various addresses and comments
   - Test `rename_local_variable()` and `rename_global_variable()`
   - Test `set_global_variable_type()` and `set_local_variable_type()`
   - Test `rename_function()` and `set_function_prototype()`
   - Test `declare_c_type()` with various C declarations
   - Verify that the changes are applied correctly in IDA Pro

6. **Debugging Functions (Unsafe)**
   - Start the server with the `--unsafe` flag
   - Test all debugging functions with a suitable binary
   - Verify that the functions work as expected

### 3. Error Handling Testing

1. **Invalid Input Testing**
   - Test functions with invalid parameters
   - Verify that appropriate error messages are returned

2. **Edge Case Testing**
   - Test functions with edge case inputs (empty strings, very large values, etc.)
   - Verify that the functions handle these cases gracefully

3. **Concurrency Testing**
   - Test multiple concurrent requests
   - Verify that the server handles concurrency correctly

### 4. Performance Testing

1. **Response Time Testing**
   - Measure response times for various functions
   - Verify that response times are acceptable

2. **Memory Usage Testing**
   - Monitor memory usage during extended usage
   - Verify that there are no memory leaks

## Test Results

### Latest Test Results

| Test Category | Test Case | Result | Notes |
|---------------|-----------|--------|-------|
| Installation | Fresh Installation | Pass | Tested on Windows, macOS, and Linux |
| Installation | Upgrade Testing | Pass | Upgraded from v1.2.0 to v1.3.0 |
| Installation | Uninstallation Testing | Pass | All components removed correctly |
| Functionality | Connection Testing | Pass | Tested with all supported clients |
| Functionality | Metadata Functions | Pass | All metadata functions working correctly |
| Functionality | Navigation Functions | Pass | All navigation functions working correctly |
| Functionality | Analysis Functions | Pass | All analysis functions working correctly |
| Functionality | Modification Functions | Pass | All modification functions working correctly |
| Functionality | Debugging Functions | Pass | All debugging functions working correctly |
| Error Handling | Invalid Input Testing | Pass | Appropriate error messages returned |
| Error Handling | Edge Case Testing | Pass | Edge cases handled gracefully |
| Error Handling | Concurrency Testing | Pass | No issues with concurrent requests |
| Performance | Response Time Testing | Pass | Response times within acceptable limits |
| Performance | Memory Usage Testing | Pass | No memory leaks detected |

### Known Issues

1. **Issue**: Some versions of IDA Pro may not support certain type system operations.
   **Workaround**: Use simpler type definitions or update to the latest version of IDA Pro.

2. **Issue**: The plugin may not load correctly if Python 3.11 or higher is not available.
   **Workaround**: Use `idapyswitch` to switch to a compatible Python version.

3. **Issue**: On macOS, the keyboard shortcut may conflict with system shortcuts.
   **Workaround**: Use the menu option (Edit -> Plugins -> MCP) instead of the keyboard shortcut.

## Reporting Issues

If you encounter any issues during testing, please report them on the [GitHub Issues page](https://github.com/mrexodia/ida-pro-mcp/issues) with the following information:

- Operating system and version
- IDA Pro version
- Python version
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or logs

## Future Test Plans

1. **Automated Testing**
   - Develop automated tests for the MCP server
   - Implement continuous integration testing

2. **Compatibility Testing**
   - Test with additional MCP clients as they become available
   - Test with future versions of IDA Pro

3. **Security Testing**
   - Conduct security audits of the codebase
   - Test for potential vulnerabilities

