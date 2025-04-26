# Getting Started

This guide will help you get started with IDA Pro MCP and show you how to perform basic tasks.

## Prerequisites

Before you begin, make sure you have:

1. Installed IDA Pro MCP following the [Installation Guide](installation.md)
2. Installed and configured a compatible MCP client (Claude, Cursor, etc.)
3. Opened IDA Pro with a binary loaded

## Starting the MCP Plugin

1. In IDA Pro, go to `Edit -> Plugins -> MCP` or press `Ctrl+Alt+M` (Windows/Linux) or `Ctrl+Option+M` (macOS).
2. You should see a message in the output window: `[MCP] Server started at http://localhost:13337`

## Basic Usage

### Checking Connection

First, verify that your MCP client can communicate with IDA Pro:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>check_connection</tool_name>
<arguments></arguments>
</use_mcp_tool>
```

If successful, you should see a message confirming the connection to IDA Pro.

### Getting Metadata

To get information about the currently loaded binary:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>get_metadata</tool_name>
<arguments></arguments>
</use_mcp_tool>
```

This will return details about the binary, such as its name, architecture, and other metadata.

### Listing Functions

To list functions in the binary:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>list_functions</tool_name>
<arguments>
{
  "offset": 0,
  "count": 10
}
</arguments>
</use_mcp_tool>
```

This will return the first 10 functions in the binary. You can adjust the `offset` and `count` parameters to navigate through the list.

### Decompiling a Function

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

### Adding Comments

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

### Renaming Functions

To rename a function:

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>rename_function</tool_name>
<arguments>
{
  "function_address": "0x140001000",
  "new_name": "authenticate_user"
}
</arguments>
</use_mcp_tool>
```

## Example Workflow

Here's an example of a typical workflow for analyzing a binary with IDA Pro MCP:

1. **Get an overview of the binary**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>get_metadata</tool_name>
   <arguments></arguments>
   </use_mcp_tool>
   ```

2. **List entry points**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>get_entry_points</tool_name>
   <arguments></arguments>
   </use_mcp_tool>
   ```

3. **Decompile the main function**:
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

4. **Analyze the function and add comments**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>set_comment</tool_name>
   <arguments>
   {
     "address": "0x140001050",
     "comment": "This function checks if the input password is correct"
   }
   </arguments>
   </use_mcp_tool>
   ```

5. **Rename functions and variables for better readability**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>rename_function</tool_name>
   <arguments>
   {
     "function_address": "0x140001050",
     "new_name": "validate_password"
   }
   </arguments>
   </use_mcp_tool>
   ```

## Prompt Engineering

When working with IDA Pro MCP, it's important to provide clear instructions to your AI assistant. Here's a sample prompt that you can use as a starting point:

```
Your task is to analyze a crackme in IDA Pro. You can use the MCP tools to retrieve information. In general use the following strategy:
- Inspect the decompilation and add comments with your findings
- Rename variables to more sensible names
- Change the variable and argument types if necessary (especially pointer and array types)
- Change function names to be more descriptive
- If more details are necessary, disassemble the function and add comments with your findings
- NEVER convert number bases yourself. Use the convert_number MCP tool if needed!
- Do not attempt brute forcing, derive any solutions purely from the disassembly and simple python scripts
- Create a report.md with your findings and steps taken at the end
- When you find a solution, prompt to user for feedback with the password you found
```

Feel free to customize this prompt based on your specific needs.

## Next Steps

Now that you're familiar with the basics of IDA Pro MCP, you can:

- Explore the [API Reference](api-reference.md) to learn about all available functions
- Check out the [Examples](examples.md) for more complex use cases
- Learn about the [Architecture](architecture.md) to understand how IDA Pro MCP works
- Contribute to the project by following the [Development Guide](development-guide.md)
