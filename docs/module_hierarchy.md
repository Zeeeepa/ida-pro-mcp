# IDA Pro MCP Module Hierarchy

## Visual Representation

```
ida_pro_mcp
│
├── server.py
│   ├── Main MCP server implementation
│   ├── Handles JSON-RPC communication with IDA plugin
│   ├── Provides MCP tools for LLM clients
│   ├── Manages MCP server installation
│   └── Manages IDA plugin installation
│
├── idalib_server.py
│   ├── Alternative server implementation using IDA library directly
│   ├── Provides direct access to IDA functionality
│   ├── Handles tool registration and documentation
│   └── Manages MCP server configuration
│
└── mcp-plugin.py
    ├── IDA Pro plugin implementation
    ├── Provides JSON-RPC server within IDA
    ├── Implements IDA-specific functionality
    ├── Handles thread synchronization for IDA operations
    └── Registers RPC methods for remote control
```

## Key Dependencies

### External Dependencies

- **mcp.server.fastmcp (FastMCP)**: Core MCP server implementation
- **IDA SDK modules**: IDA Pro SDK for plugin development
  - ida_hexrays: Decompiler functionality
  - ida_kernwin: UI functionality
  - ida_funcs: Function handling
  - ida_gdl: Graph functionality
  - ida_lines: Line handling
  - ida_idaapi: Core IDA API
  - And many others

### Internal Dependencies

- **server.py** → **mcp-plugin.py**: Server uses the plugin code to generate MCP tools
- **idalib_server.py** → **mcp-plugin.py**: IDA library server imports the plugin for RPC methods

## Module Responsibilities

### server.py

- Initializes the MCP server
- Generates MCP tools from the IDA plugin
- Handles JSON-RPC communication with the IDA plugin
- Manages MCP server installation for various clients
- Manages IDA plugin installation

### idalib_server.py

- Provides an alternative server implementation using IDA library directly
- Handles tool registration and documentation
- Manages MCP server configuration
- Initializes IDA library and decompiler

### mcp-plugin.py

- Implements the IDA Pro plugin
- Provides JSON-RPC server within IDA
- Implements IDA-specific functionality
- Handles thread synchronization for IDA operations
- Registers RPC methods for remote control

## Data Flow

1. **LLM Client** → **MCP Server (server.py)**: Client sends a request to the MCP server
2. **MCP Server (server.py)** → **IDA Plugin (mcp-plugin.py)**: Server forwards the request to the IDA plugin
3. **IDA Plugin (mcp-plugin.py)** → **IDA SDK**: Plugin uses IDA SDK to perform the requested operation
4. **IDA SDK** → **IDA Plugin (mcp-plugin.py)**: SDK returns the result to the plugin
5. **IDA Plugin (mcp-plugin.py)** → **MCP Server (server.py)**: Plugin returns the result to the server
6. **MCP Server (server.py)** → **LLM Client**: Server returns the result to the client

## Alternative Flow (idalib_server.py)

1. **LLM Client** → **MCP Server (idalib_server.py)**: Client sends a request to the MCP server
2. **MCP Server (idalib_server.py)** → **IDA Library**: Server uses IDA library directly
3. **IDA Library** → **MCP Server (idalib_server.py)**: Library returns the result to the server
4. **MCP Server (idalib_server.py)** → **LLM Client**: Server returns the result to the client

