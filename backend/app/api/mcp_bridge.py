from fastapi import APIRouter, HTTPException, Query
from app.schemas.mcp_bridge import McpJsonRpcRequest, McpJsonRpcResponse, McpPromptGetResponse, McpPromptListResponse, McpResourceListResponse, McpResourceReadResponse, McpToolCallRequest, McpToolCallResponse, McpToolListResponse
from app.services.mcp_bridge_service import call_mcp_tool, get_mcp_prompt, handle_mcp_json_rpc, list_mcp_prompts, list_mcp_resources, list_mcp_tools, read_mcp_resource

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/tools", response_model=McpToolListResponse)
def get_mcp_tools():
    return McpToolListResponse(tools=list_mcp_tools())

@router.post("/tools/call", response_model=McpToolCallResponse)
def call_tool(request: McpToolCallRequest):
    result = call_mcp_tool(request.name, request.arguments)
    return McpToolCallResponse(**result)

@router.get("/resources", response_model=McpResourceListResponse)
def get_mcp_resources():
    return McpResourceListResponse(resources=list_mcp_resources())

@router.get("/resources/read", response_model=McpResourceReadResponse)
def read_resource(uri: str = Query(..., min_length=1)):
    try:
        result = read_mcp_resource(uri)
        return McpResourceReadResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.get("/prompts", response_model=McpPromptListResponse)
def get_mcp_prompts():
    return McpPromptListResponse(prompts=list_mcp_prompts())

@router.get("/prompts/{prompt_name}", response_model=McpPromptGetResponse)
def get_prompt(prompt_name: str):
    try:
        result = get_mcp_prompt(prompt_name)
        return McpPromptGetResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.post("/json-rpc", response_model=McpJsonRpcResponse)
def mcp_json_rpc(request: McpJsonRpcRequest):
    result = handle_mcp_json_rpc(request.model_dump())
    return McpJsonRpcResponse(**result)
