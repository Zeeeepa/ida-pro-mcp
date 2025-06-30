# Overview

## What is IDA Pro MCP?

IDA Pro MCP is a Model Context Protocol (MCP) server that enables AI-assisted reverse engineering in IDA Pro. It allows AI tools like Claude, Cursor, and other MCP-compatible clients to interact with IDA Pro, providing capabilities for binary analysis, code decompilation, and IDB modification.

The project implements the [Model Context Protocol](https://modelcontextprotocol.io/introduction), which is becoming a standard for AI tool integration, making it compatible with various AI clients.

## What is "Vibe Reversing"?

"Vibe reversing" refers to a modern approach to reverse engineering that leverages AI assistance to enhance productivity and understanding. By connecting AI tools to IDA Pro through the MCP protocol, reverse engineers can:

- Get AI assistance in understanding complex code
- Automatically rename variables and functions with meaningful names
- Add helpful comments to decompiled code
- Identify patterns and potential vulnerabilities
- Perform more efficient analysis of binaries

This approach combines the power of AI with the expertise of human reverse engineers, creating a more efficient and effective workflow.

## Key Features

- **Easy Installation**: Automated installation process for both the MCP server and IDA plugin
- **Comprehensive API**: Rich set of functions for interacting with IDA Pro
- **Multi-Client Support**: Compatible with various MCP clients like Cline, Roo Code, Claude, Cursor, etc.
- **Extensible Architecture**: Simple design that makes it easy to add new functionality
- **Secure Design**: Clear separation between read-only and write operations
- **Open Source**: MIT-licensed code that can be freely used and modified

## Use Cases

IDA Pro MCP is designed for a variety of reverse engineering tasks, including:

- **Malware Analysis**: Quickly understand the behavior and structure of malicious code
- **Vulnerability Research**: Identify potential security issues in binaries
- **Software Interoperability**: Understand undocumented APIs and protocols
- **Legacy Code Analysis**: Make sense of old, poorly documented code
- **CTF Challenges**: Solve reverse engineering challenges more efficiently

## High-Level Architecture

The system consists of two main components:

1. **MCP Server**: A Python-based server that implements the Model Context Protocol and communicates with IDA Pro
2. **IDA Pro Plugin**: A plugin that exposes IDA Pro functionality via JSON-RPC

These components work together to provide a bridge between AI tools and IDA Pro:

```
+----------------+       +----------------+       +----------------+
|                |       |                |       |                |
|   MCP Client   | <---> |   MCP Server   | <---> |    IDA Pro     |
| (Claude, etc.) |       | (ida-pro-mcp)  |       |  (with plugin) |
|                |       |                |       |                |
+----------------+       +----------------+       +----------------+
```

The MCP client sends requests to the MCP server, which translates them into JSON-RPC calls to the IDA Pro plugin. The plugin executes the requested operations in IDA Pro and returns the results back through the same channel.

## Getting Started

To get started with IDA Pro MCP, see the [Installation Guide](installation.md) and [Getting Started Guide](getting-started.md).
