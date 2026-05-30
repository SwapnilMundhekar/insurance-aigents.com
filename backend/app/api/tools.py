from fastapi import APIRouter
from app.schemas.tools import ToolExecuteRequest, ToolExecuteResponse, ToolListResponse
from app.services.tool_registry_service import execute_tool, list_tools

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("/list", response_model=ToolListResponse)
def get_tools():
    return ToolListResponse(tools=list_tools())

@router.post("/execute", response_model=ToolExecuteResponse)
def run_tool(request: ToolExecuteRequest):
    result = execute_tool(request.tool_name, request.tool_input)
    return ToolExecuteResponse(**result)