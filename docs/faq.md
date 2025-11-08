# Frequently Asked Questions

## General Questions

### What is IDA Pro MCP?

IDA Pro MCP is a Model Context Protocol (MCP) server that enables AI-assisted reverse engineering in IDA Pro. It allows AI tools like Claude, Cursor, and other MCP-compatible clients to interact with IDA Pro, providing capabilities for binary analysis, code decompilation, and IDB modification.

### What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is a standardized way for AI tools to interact with external systems. It allows AI models to access data and functionality from various sources, making them more powerful and versatile. In the context of IDA Pro MCP, it enables AI tools to interact with IDA Pro for reverse engineering tasks.

### What is "vibe reversing"?

"Vibe reversing" refers to a modern approach to reverse engineering that leverages AI assistance to enhance productivity and understanding. By connecting AI tools to IDA Pro through the MCP protocol, reverse engineers can get AI assistance in understanding complex code, automatically rename variables and functions with meaningful names, add helpful comments to decompiled code, and more.

### Which MCP clients are supported?

IDA Pro MCP supports various MCP clients, including:
- [Cline](https://cline.bot)
- [Roo Code](https://roocode.com)
- [Claude](https://claude.ai/download)
- [Cursor](https://cursor.com)
- [VSCode Agent Mode](https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated/)
- Other MCP-compatible clients

### What are the system requirements?

- [Python](https://www.python.org/downloads/) (version 3.11 or higher)
- [IDA Pro](https://hex-rays.com/ida-pro) (version 8.3 or higher, version 9 recommended)
- A supported MCP client

## Installation and Setup

### How do I install IDA Pro MCP?

The easiest way to install IDA Pro MCP is using the automated installation script:

1. Install the IDA Pro MCP package:
   ```sh
   pip install --upgrade git+https://github.com/mrexodia/ida-pro-mcp
   ```

2. Configure the MCP servers and install the IDA Plugin:
   ```sh
   ida-pro-mcp --install
   ```

3. Restart IDA Pro, Visual Studio Code, Claude, or any other MCP client you're using.

For more detailed instructions, see the [Installation Guide](installation.md).

### Do I need to restart my MCP client after installation?

Yes, you need to completely restart your MCP client after installing IDA Pro MCP. This is especially important for Claude, which runs in the background and needs to be quit from the tray icon.

### Can I use IDA Pro MCP with the free version of IDA?

Yes, you can use IDA Pro MCP with the free version of IDA, but some functionality might be limited. For example, the Hex-Rays decompiler is not included in the free version, so the `decompile_function` tool won't work.

### How do I start the MCP plugin in IDA Pro?

In IDA Pro, go to `Edit -> Plugins -> MCP` or press `Ctrl+Alt+M` (Windows/Linux) or `Ctrl+Option+M` (macOS). You should see a message in the output window: `[MCP] Server started at http://localhost:13337`.

## Usage

### How do I check if the connection is working?

You can use the `check_connection` tool to verify that your MCP client can communicate with IDA Pro:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>check_connection</tool_name>
<arguments></arguments>
</use_mcp_tool>
```

If successful, you should see a message confirming the connection to IDA Pro.

### How do I decompile a function?

To decompile a function, you need its address:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>decompile_function</tool_name>
<arguments>
{
  "address": "0x140001000"
}
</arguments>
</use_mcp_tool>
```

Replace `0x140001000` with the actual address of the function you want to decompile.

### How do I rename a function?

To rename a function:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>rename_function</tool_name>
<arguments>
{
  "function_address": "0x140001000",
  "new_name": "new_function_name"
}
</arguments>
</use_mcp_tool>
```

### How do I add comments to the code?

To add a comment to a specific address:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>set_comment</tool_name>
<arguments>
{
  "address": "0x140001000",
  "comment": "This is an important function that handles user authentication"
}
</arguments>
</use_mcp_tool>
```

### Can I use IDA Pro MCP for debugging?

Yes, IDA Pro MCP includes several debugging functions, but they are marked as unsafe and are only available when the `--unsafe` flag is used. These functions include:
- `dbg_get_registers`: Get all registers and their values
- `dbg_get_call_stack`: Get the current call stack
- `dbg_list_breakpoints`: List all breakpoints in the program
- `dbg_start_process`: Start the debugger
- `dbg_exit_process`: Exit the debugger
- `dbg_continue_process`: Continue the debugger
- `dbg_run_to`: Run the debugger to the specified address
- `dbg_set_breakpoint`: Set a breakpoint at the specified address
- `dbg_delete_breakpoint`: Delete a breakpoint at the specified address
- `dbg_enable_breakpoint`: Enable or disable a breakpoint at the specified address

## Troubleshooting

### The MCP client cannot connect to IDA Pro. What should I do?

Make sure you've started the MCP plugin in IDA Pro by clicking `Edit -> Plugins -> MCP` or pressing `Ctrl+Alt+M` (Windows/Linux) or `Ctrl+Option+M` (macOS). Check the IDA Pro output window for a message like `[MCP] Server started at http://localhost:13337`.

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).

### The decompilation fails. What could be the issue?

There are several possible causes:
1. You might not have the Hex-Rays decompiler installed and licensed.
2. The address you're providing might not be a valid function address.
3. The function might be too complex or obfuscated for the decompiler to handle.

Try using the `disassemble_function` tool instead, which provides the assembly code for the function.

### How do I report a bug or request a feature?

If you've found a bug or have a feature request, you can [open an issue](https://github.com/mrexodia/ida-pro-mcp/issues) on GitHub.

## Development

### How do I add a new function to IDA Pro MCP?

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

For more detailed instructions, see the [Development Guide](development-guide.md).

### How do I contribute to the project?

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request

Please follow the existing code style and add appropriate documentation for your changes.

### What is the license for IDA Pro MCP?

IDA Pro MCP is licensed under the MIT License. See the `LICENSE` file for details.
