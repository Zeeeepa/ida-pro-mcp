# Installation Guide

This guide will walk you through the process of installing and configuring IDA Pro MCP.

## Prerequisites

Before installing IDA Pro MCP, ensure you have the following:

- [Python](https://www.python.org/downloads/) (version 3.11 or higher)
  - If using IDA Pro, use `idapyswitch` to switch to the newest Python version
- [IDA Pro](https://hex-rays.com/ida-pro) (version 8.3 or higher, version 9 recommended)
- A supported MCP Client (pick one you like):
  - [Cline](https://cline.bot)
  - [Roo Code](https://roocode.com)
  - [Claude](https://claude.ai/download)
  - [Cursor](https://cursor.com)
  - [VSCode Agent Mode](https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated/)
  - [Other MCP Clients](https://modelcontextprotocol.io/clients#example-clients)

## Automated Installation

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

> **Important**: Make sure you completely restart IDA/Visual Studio Code/Claude for the installation to take effect. Claude runs in the background and you need to quit it from the tray icon.

## Manual Installation

If you prefer to install IDA Pro MCP manually, follow these steps:

### 1. Install the MCP Server

1. Install [uv](https://github.com/astral-sh/uv) globally:
   - Windows: `pip install uv`
   - Linux/Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. Clone the repository:
   ```sh
   git clone https://github.com/mrexodia/ida-pro-mcp.git
   cd ida-pro-mcp
   ```

3. Configure your MCP client:

#### For Cline/Roo Code:

1. Navigate to the Cline/Roo Code _MCP Servers_ configuration.
2. Click on the _Installed_ tab.
3. Click on _Configure MCP Servers_, which will open `cline_mcp_settings.json`.
4. Add the `ida-pro-mcp` server:

```json
{
  "mcpServers": {
    "github.com/mrexodia/ida-pro-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\MCP\\ida-pro-mcp",
        "run",
        "server.py",
        "--install-plugin"
      ],
      "timeout": 1800,
      "disabled": false,
      "autoApprove": [
        "check_connection",
        "get_metadata",
        "get_function_by_name",
        "get_function_by_address",
        "get_current_address",
        "get_current_function",
        "convert_number",
        "list_functions",
        "list_strings",
        "search_strings",
        "decompile_function",
        "disassemble_function",
        "get_xrefs_to",
        "get_entry_points",
        "set_comment",
        "rename_local_variable",
        "rename_global_variable",
        "set_global_variable_type",
        "rename_function",
        "set_function_prototype",
        "declare_c_type",
        "set_local_variable_type"
      ],
      "alwaysAllow": [
        "check_connection",
        "get_metadata",
        "get_function_by_name",
        "get_function_by_address",
        "get_current_address",
        "get_current_function",
        "convert_number",
        "list_functions",
        "list_strings",
        "search_strings",
        "decompile_function",
        "disassemble_function",
        "get_xrefs_to",
        "get_entry_points",
        "set_comment",
        "rename_local_variable",
        "rename_global_variable",
        "set_global_variable_type",
        "rename_function",
        "set_function_prototype",
        "declare_c_type",
        "set_local_variable_type"
      ]
    }
  }
}
```

> Note: Adjust the `--directory` path to match your actual installation directory.

### 2. Install the IDA Plugin

1. Locate your IDA Pro plugins folder:
   - Windows: `%APPDATA%\Hex-Rays\IDA Pro\plugins`
   - Linux/Mac: `~/.idapro/plugins`

2. Copy (do not move) `src/ida_pro_mcp/mcp-plugin.py` to your plugins folder.

3. Open an IDB in IDA Pro and click `Edit -> Plugins -> MCP` to start the server.

## Verification

To verify that the installation was successful:

1. Open IDA Pro and load a binary.
2. Start the MCP plugin by clicking `Edit -> Plugins -> MCP` (or using the shortcut `Ctrl+Alt+M`).
3. In your MCP client (e.g., Claude, Cursor), test the connection with:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>check_connection</tool_name>
<arguments></arguments>
</use_mcp_tool>
```

If the connection is successful, you should see a message confirming the connection to IDA Pro.

## Troubleshooting

If you encounter issues during installation:

- **Plugin not loading**: Make sure you're using Python 3.11 or higher. Use `idapyswitch` to switch to the correct Python version.
- **Connection errors**: Ensure that the MCP plugin is running in IDA Pro. Check if you see the message "[MCP] Server started at http://localhost:13337" in the IDA Pro output window.
- **Configuration issues**: Verify that the MCP server configuration in your client matches the expected format.
- **Port conflicts**: If port 13337 is already in use, you may need to modify the port in the plugin code.

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).
