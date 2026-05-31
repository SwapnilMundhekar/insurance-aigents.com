# MCP Integration

MCP means Model Context Protocol. It is a standard pattern for exposing tools, resources, and prompts to AI systems.

## Current implementation

This project implements a local MCP bridge layer that exposes approved insurance tools through MCP-style endpoints and JSON-RPC methods.

## Why this is useful

The Agentic RAG supervisor no longer needs to call the internal tool registry directly. It calls a client adapter, and the adapter routes the request through the MCP bridge.

## Flow

```text
Supervisor Agent
    ↓
MCP Client Adapter
    ↓
MCP Bridge Layer
    ↓
Approved Insurance Tools
```

## Endpoints

- `GET /mcp/tools`
- `POST /mcp/tools/call`
- `GET /mcp/resources`
- `GET /mcp/resources/read`
- `GET /mcp/prompts`
- `GET /mcp/prompts/{prompt_name}`
- `POST /mcp/json-rpc`

## JSON-RPC examples

List tools:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Call a tool:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "coverage_check_tool",
    "arguments": {
      "query": "The customer has windscreen damage after a storm."
    }
  }
}
```

## Production direction

The next production step is to expose the same tools through an official MCP server transport while keeping input governance, output guardrails, audit persistence, and observability around every tool call.
