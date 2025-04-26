# Troubleshooting

This guide provides solutions to common issues you might encounter when using IDA Pro MCP.

## Connection Issues

### MCP Client Cannot Connect to IDA Pro

**Symptoms**: The MCP client (Claude, Cursor, etc.) cannot connect to IDA Pro, and you see an error message when using the `check_connection` tool.

**Possible Causes and Solutions**:

1. **IDA Pro Plugin Not Running**
   - Make sure you've started the MCP plugin in IDA Pro by clicking `Edit -> Plugins -> MCP` or pressing `Ctrl+Alt+M` (Windows/Linux) or `Ctrl+Option+M` (macOS).
   - Check the IDA Pro output window for a message like `[MCP] Server started at http://localhost:13337`.

2. **Port Already in Use**
   - If you see an error message like `[MCP] Error: Port 13337 is already in use`, another process is using the same port.
   - Close any other instances of IDA Pro or applications that might be using port 13337.
   - Alternatively, you can modify the port in the plugin code.

3. **Firewall Blocking Connection**
   - Check if your firewall is blocking the connection.
   - Add an exception for IDA Pro or temporarily disable the firewall for testing.

4. **Incorrect MCP Server Configuration**
   - Verify that the MCP server configuration in your client matches the expected format.
   - Check the server name in your MCP client tool calls (`github.com/mrexodia/ida-pro-mcp`).

### MCP Server Installation Issues

**Symptoms**: The MCP server installation fails or doesn't work correctly.

**Possible Causes and Solutions**:

1. **Python Version Mismatch**
   - Ensure you're using Python 3.11 or higher.
   - Use `python --version` to check your Python version.
   - If using IDA Pro, use `idapyswitch` to switch to the correct Python version.

2. **Missing Dependencies**
   - Make sure all dependencies are installed:
     ```sh
     pip install --upgrade mcp>=1.6.0
     ```

3. **Permission Issues**
   - Run the installation commands with administrator privileges if needed.
   - Check if you have write permissions to the installation directories.

4. **Incorrect Installation Path**
   - Verify that the installation paths are correct for your operating system.
   - Check the MCP server configuration file for correct paths.

## IDA Pro Plugin Issues

### Plugin Not Loading

**Symptoms**: The MCP plugin doesn't appear in the IDA Pro plugins menu.

**Possible Causes and Solutions**:

1. **Plugin Not Installed Correctly**
   - Verify that the plugin file (`mcp-plugin.py`) is in the correct IDA Pro plugins folder:
     - Windows: `%APPDATA%\Hex-Rays\IDA Pro\plugins`
     - Linux/Mac: `~/.idapro/plugins`

2. **Python Version Mismatch**
   - IDA Pro MCP requires Python 3.11 or higher.
   - Use `idapyswitch` to switch to the correct Python version.

3. **Missing Dependencies**
   - Make sure all required Python packages are installed in the IDA Pro Python environment.

4. **IDA Pro Version Incompatibility**
   - Ensure you're using IDA Pro 8.3 or higher (version 9 recommended).

### Plugin Crashes

**Symptoms**: IDA Pro crashes or freezes when using the MCP plugin.

**Possible Causes and Solutions**:

1. **Incompatible IDA Pro Version**
   - Verify that you're using a compatible version of IDA Pro (8.3 or higher).

2. **Large Binary Files**
   - When working with very large binary files, IDA Pro might become unresponsive.
   - Try using smaller binary files for testing.

3. **Memory Issues**
   - Close unnecessary applications to free up memory.
   - Restart IDA Pro and try again.

## Function-Specific Issues

### Decompilation Fails

**Symptoms**: The `decompile_function` tool fails to decompile a function.

**Possible Causes and Solutions**:

1. **Hex-Rays Decompiler Not Available**
   - Ensure that you have the Hex-Rays decompiler installed and licensed.
   - The decompiler is a separate product from IDA Pro.

2. **Invalid Function Address**
   - Verify that the address you're providing is a valid function address.
   - Use the `list_functions` tool to get a list of valid function addresses.

3. **Complex or Obfuscated Code**
   - Some functions might be too complex or obfuscated for the decompiler to handle.
   - Try disassembling the function instead using the `disassemble_function` tool.

### Renaming Functions or Variables Fails

**Symptoms**: The `rename_function` or `rename_local_variable` tools fail to rename a function or variable.

**Possible Causes and Solutions**:

1. **Invalid Name**
   - Ensure that the new name follows IDA Pro's naming conventions.
   - Avoid using special characters or reserved keywords.

2. **Name Already in Use**
   - The new name might already be in use by another function or variable.
   - Choose a different name or check for naming conflicts.

3. **Invalid Function or Variable**
   - Verify that the function address or variable name is correct.
   - Use the `list_functions` tool to get a list of valid function addresses.

## MCP Client-Specific Issues

### Claude Issues

**Symptoms**: Claude doesn't recognize or execute MCP tools correctly.

**Possible Causes and Solutions**:

1. **Incorrect Tool Format**
   - Ensure that you're using the correct format for MCP tool calls in Claude:
     ```
     <use_mcp_tool>
     <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
     <tool_name>check_connection</tool_name>
     <arguments></arguments>
     </use_mcp_tool>
     ```

2. **Claude Not Restarted After Installation**
   - Claude runs in the background and needs to be completely restarted after installing the MCP server.
   - Quit Claude from the tray icon and restart it.

### Cursor Issues

**Symptoms**: Cursor doesn't recognize or execute MCP tools correctly.

**Possible Causes and Solutions**:

1. **Incorrect Tool Format**
   - Ensure that you're using the correct format for MCP tool calls in Cursor.

2. **Cursor Not Restarted After Installation**
   - Restart Cursor after installing the MCP server.

3. **MCP Configuration Issues**
   - Check the MCP configuration in Cursor's settings.

## Advanced Troubleshooting

### Debugging the MCP Server

To get more detailed information about what's happening with the MCP server, you can run it with the `--verbose` flag:

```sh
ida-pro-mcp --verbose
```

This will output more detailed logs that can help identify the issue.

### Debugging the IDA Pro Plugin

To debug the IDA Pro plugin, you can add print statements to the plugin code that will appear in the IDA Pro output window:

```python
print("[MCP Debug] Some debug information")
```

### Manual JSON-RPC Testing

You can test the JSON-RPC interface directly by sending HTTP requests to the plugin:

```sh
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "get_metadata", "params": [], "id": 1}' http://localhost:13337/mcp
```

This can help identify if the issue is with the MCP server or the IDA Pro plugin.

## Getting Help

If you're still experiencing issues after trying the solutions above, you can:

1. **Check the GitHub Repository**: Visit the [IDA Pro MCP GitHub repository](https://github.com/mrexodia/ida-pro-mcp) for the latest updates and known issues.

2. **Open an Issue**: If you've found a bug or have a feature request, you can [open an issue](https://github.com/mrexodia/ida-pro-mcp/issues) on GitHub.

3. **Contact the Developer**: You can reach out to the developer through GitHub or other channels mentioned in the repository.
