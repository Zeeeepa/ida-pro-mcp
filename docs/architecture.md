# IDA Pro MCP Architecture

## Overview

The IDA Pro MCP project provides a Model Context Protocol (MCP) server that enables AI assistants to interact with IDA Pro for reverse engineering tasks. The architecture consists of several key components that work together to provide this functionality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client                               │
│ (Claude, Cline, Roo Code, Cursor, VSCode Agent Mode, etc.)      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server (FastMCP)                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 ida_pro_mcp.server.py                   │    │
│  │                                                         │    │
│  │  - Handles MCP protocol communication                   │    │
│  │  - Registers tools from mcp-plugin.py                   │    │
│  │  - Forwards requests to IDA Pro plugin                  │    │
│  └─────────────────────────────┬───────────────────────────┘    │
│                                │                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    JSON-RPC Communication                       │
│                 (HTTP Server on localhost:13337)                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       IDA Pro Plugin                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               ida_pro_mcp.mcp-plugin.py                 │    │
│  │                                                         │    │
│  │  - Implements JSON-RPC server                           │    │
│  │  - Provides IDA Pro API functions                       │    │
│  │  - Handles thread synchronization                       │    │
│  │  - Manages IDA Pro interaction                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. MCP Client

External AI assistants that support the Model Context Protocol, such as:
- Claude
- Cline
- Roo Code
- Cursor
- VSCode Agent Mode
- Other MCP-compatible clients

### 2. MCP Server (server.py)

The main server component that:
- Implements the Model Context Protocol using FastMCP
- Registers tools from the IDA Pro plugin
- Handles communication between MCP clients and the IDA Pro plugin
- Manages installation of the IDA Pro plugin
- Provides configuration for various MCP clients

### 3. JSON-RPC Communication Layer

A lightweight HTTP server that:
- Runs on localhost:13337
- Handles JSON-RPC requests from the MCP server
- Forwards requests to the IDA Pro plugin
- Returns results back to the MCP server

### 4. IDA Pro Plugin (mcp-plugin.py)

The plugin that runs within IDA Pro and:
- Implements a JSON-RPC server to receive commands
- Provides functions to interact with IDA Pro's API
- Handles thread synchronization for safe IDA Pro operations
- Manages decompilation, analysis, and modification of binary code

### 5. IDALib Server (idalib_server.py)

An alternative server implementation that:
- Allows running the MCP server with idalib (headless IDA)
- Provides the same functionality without the IDA Pro GUI
- Useful for automated analysis or server environments

## Data Flow

1. An MCP client (like Claude) sends a request to perform an IDA Pro operation
2. The MCP server (server.py) receives the request and forwards it to the IDA Pro plugin
3. The JSON-RPC server in the IDA Pro plugin receives the request
4. The plugin executes the requested operation in IDA Pro
5. Results are returned through the JSON-RPC server back to the MCP server
6. The MCP server formats the response and sends it back to the MCP client

## Module Dependencies

- **server.py**: Depends on FastMCP and communicates with mcp-plugin.py
- **mcp-plugin.py**: Depends on IDA Pro API (ida_*) modules
- **idalib_server.py**: Depends on idalib and mcp-plugin.py

## Security Considerations

- The MCP server includes a concept of "unsafe" functions that are disabled by default
- These functions can be enabled with the `--unsafe` flag for advanced operations
- The server runs locally and only accepts connections from localhost
- Authentication is handled by the MCP client

