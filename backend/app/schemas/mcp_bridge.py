from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class McpToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class McpToolListResponse(BaseModel):
    tools: List[McpToolDefinition]

class McpToolCallRequest(BaseModel):
    name: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = {}

class McpToolCallResponse(BaseModel):
    name: str
    ok: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    transport: str

class McpResourceDefinition(BaseModel):
    uri: str
    name: str
    description: str
    mimeType: str

class McpResourceListResponse(BaseModel):
    resources: List[McpResourceDefinition]

class McpResourceReadResponse(BaseModel):
    uri: str
    mimeType: str
    text: str

class McpPromptDefinition(BaseModel):
    name: str
    description: str
    arguments: List[Dict[str, Any]]

class McpPromptListResponse(BaseModel):
    prompts: List[McpPromptDefinition]

class McpPromptGetResponse(BaseModel):
    name: str
    description: str
    prompt: str

class McpJsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Dict[str, Any] = {}

class McpJsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
