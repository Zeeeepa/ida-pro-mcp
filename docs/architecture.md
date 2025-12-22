# Architecture

This document describes the architecture of IDA Pro MCP, explaining how the different components work together to provide AI-assisted reverse engineering capabilities.

## Overview

IDA Pro MCP consists of several key components that work together:

1. **MCP Server**: A Python-based server that implements the Model Context Protocol
2. **IDA Pro Plugin**: A plugin that exposes IDA Pro functionality via JSON-RPC
3. **MCP Client**: An external AI tool that communicates with the MCP server

The architecture follows a client-server model, where the MCP client sends requests to the MCP server, which then communicates with IDA Pro through the plugin.

## Component Diagram

```
+----------------+       +----------------+       +----------------+
|                |       |                |       |                |
|   MCP Client   | <---> |   MCP Server   | <---> |    IDA Pro     |
| (Claude, etc.) |       | (ida-pro-mcp)  |       |  (with plugin) |
|                |       |                |       |                |
+----------------+       +----------------+       +----------------+
      ^                        ^                        ^
      |                        |                        |
      v                        v                        v
+----------------+       +----------------+       +----------------+
|                |       |                |       |                |
|  User Interface|       | Model Context  |       |   JSON-RPC     |
|                |       |   Protocol     |       |                |
+----------------+       +----------------+       +----------------+
```

## Communication Flow

1. The user interacts with an MCP client (e.g., Claude, Cursor)
2. The MCP client sends a request to the MCP server using the Model Context Protocol
3. The MCP server translates the request into a JSON-RPC call
4. The JSON-RPC call is sent to the IDA Pro plugin
5. The IDA Pro plugin executes the requested operation in IDA Pro
6. The result is sent back through the same channel to the MCP client
7. The MCP client displays the result to the user

## Component Details

### MCP Server (server.py)

The MCP server is implemented in `server.py` and is responsible for:

- Implementing the Model Context Protocol
- Translating MCP requests into JSON-RPC calls
- Communicating with the IDA Pro plugin
- Handling installation and configuration

The server uses the `FastMCP` library to implement the Model Context Protocol, which allows it to communicate with MCP clients.

Key classes and functions:

- `FastMCP`: The main class that implements the MCP protocol
- `make_jsonrpc_request`: Function to send JSON-RPC requests to the IDA Pro plugin
- `MCPVisitor`: Class that processes the IDA Pro plugin code to generate MCP tools

### IDA Pro Plugin (mcp-plugin.py)

The IDA Pro plugin is implemented in `mcp-plugin.py` and is responsible for:

- Exposing IDA Pro functionality via JSON-RPC
- Executing operations in IDA Pro
- Returning results to the MCP server

The plugin uses a custom JSON-RPC implementation to handle requests from the MCP server.

Key classes and functions:

- `RPCRegistry`: Class that manages JSON-RPC methods
- `jsonrpc`: Decorator to register a function as a JSON-RPC method
- `unsafe`: Decorator to mark a function as unsafe
- `JSONRPCRequestHandler`: HTTP request handler for JSON-RPC requests
- `Server`: Class that manages the HTTP server
- `MCP`: IDA Pro plugin class

### IDALib Server (idalib_server.py)

The IDALib server is an alternative implementation that uses the `idalib` library to interact with IDA Pro without requiring the IDA Pro GUI. This is useful for automated analysis or when running in a headless environment.

Key functions:

- `fixup_tool_argument_descriptions`: Function to add parameter descriptions to MCP tools
- `main`: Main function that initializes the server and IDA Pro

## Security Considerations

IDA Pro MCP includes several security features:

1. **Function Safety**: Functions are marked as safe or unsafe, with unsafe functions requiring explicit enabling
2. **Local Operation**: The MCP server and IDA Pro plugin run locally, minimizing network exposure
3. **Controlled Access**: The MCP server only exposes specific functions to MCP clients

## Extension Points

IDA Pro MCP is designed to be easily extensible:

1. **Adding New Functions**: New functions can be added to the IDA Pro plugin by simply adding a new function with the `@jsonrpc` decorator
2. **Custom MCP Clients**: Any MCP-compatible client can be used with IDA Pro MCP
3. **Alternative Implementations**: The architecture allows for alternative implementations, such as the IDALib server

## Performance Considerations

The architecture is designed to be efficient:

1. **Lightweight Communication**: JSON-RPC provides a lightweight communication mechanism
2. **Minimal Overhead**: The MCP server adds minimal overhead to the communication between the MCP client and IDA Pro
3. **Asynchronous Operation**: The IDA Pro plugin uses threading to avoid blocking the IDA Pro UI

## Deployment

IDA Pro MCP can be deployed in several ways:

1. **Standard Installation**: The MCP server and IDA Pro plugin are installed on the same machine as IDA Pro
2. **Remote Installation**: The MCP server can be installed on a different machine than IDA Pro, with communication over HTTP
3. **Headless Installation**: The IDALib server can be used for headless operation without the IDA Pro GUI

## Future Directions

The architecture is designed to support future enhancements:

1. **Additional MCP Clients**: Support for new MCP clients as they become available
2. **Enhanced Functionality**: Addition of new functions to the IDA Pro plugin
3. **Integration with Other Tools**: Integration with other reverse engineering tools
4. **Performance Optimizations**: Further optimization of the communication between components
