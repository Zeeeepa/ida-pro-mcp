# IDA Pro MCP Modules

This document provides detailed information about each module in the IDA Pro MCP project.

## Module Overview

The IDA Pro MCP project consists of the following key modules:

1. **server.py** - The main MCP server implementation
2. **mcp-plugin.py** - The IDA Pro plugin that provides the core functionality
3. **idalib_server.py** - An alternative server implementation for headless operation

## 1. server.py

### Purpose
The `server.py` module serves as the main entry point for the MCP server. It handles communication between MCP clients and the IDA Pro plugin.

### Key Functions

- **make_jsonrpc_request()**: Makes JSON-RPC requests to the IDA plugin
- **check_connection()**: Verifies the connection to the IDA plugin
- **MCPVisitor class**: Parses the IDA plugin code to extract function definitions
- **install_mcp_servers()**: Configures MCP servers for various clients
- **install_ida_plugin()**: Installs the IDA Pro plugin
- **main()**: Entry point for the command-line interface

### Usage

The server can be started with various command-line options:
```
ida-pro-mcp [--install] [--uninstall] [--transport TRANSPORT] [--ida-rpc IDA_RPC] [--unsafe]
```

## 2. mcp-plugin.py

### Purpose
The `mcp-plugin.py` module is the IDA Pro plugin that implements the JSON-RPC server and provides functions to interact with IDA Pro.

### Key Components

- **RPCRegistry class**: Manages the registration of JSON-RPC methods
- **JSONRPCRequestHandler class**: Handles HTTP requests for JSON-RPC
- **Server class**: Implements the HTTP server for JSON-RPC
- **Thread synchronization utilities**: Ensures thread-safe operations in IDA Pro
- **JSON-RPC methods**: Various functions to interact with IDA Pro

### Available Functions

The plugin provides numerous functions for interacting with IDA Pro, including:

- Getting metadata about the current IDB
- Retrieving and manipulating functions
- Decompiling and disassembling code
- Managing comments and variable names
- Setting types and prototypes
- Debugging operations (when enabled with --unsafe)

## 3. idalib_server.py

### Purpose
The `idalib_server.py` module provides an alternative server implementation that works with idalib (headless IDA).

### Key Functions

- **fixup_tool_argument_descriptions()**: Enhances tool metadata with documentation
- **main()**: Entry point for the idalib server

### Usage

The idalib server can be started with:
```
idalib-mcp [--verbose] [--host HOST] [--port PORT] [--unsafe] input_path
```

## Module Dependencies

### External Dependencies
- **mcp**: The Model Context Protocol Python SDK
- **ida_***: IDA Pro API modules
- **http.server**: Standard library for HTTP server implementation
- **threading**: Standard library for thread management

### Internal Dependencies
- **server.py** depends on **mcp-plugin.py** for function definitions
- **idalib_server.py** depends on **mcp-plugin.py** for function implementations
- Both servers communicate with IDA Pro through JSON-RPC

## Extension Points

The architecture is designed for easy extension:

1. To add a new function to the MCP server, simply add a new function with the `@jsonrpc` decorator in `mcp-plugin.py`
2. The function will be automatically discovered and made available through the MCP server
3. For potentially dangerous functions, add the `@unsafe` decorator to disable them by default

