from fastapi import FastAPI
from app.mcp_server.tools import (
    list_assets,
    get_asset_details,
    list_data_sources,
    get_time_series_data,
    summarize_trend,
    compare_assets,
    explain_change
)

app = FastAPI(title="Financial DWH MCP Server")


TOOLS = {
    "list_assets": list_assets,
    "get_asset_details": get_asset_details,
    "list_data_sources": list_data_sources,
    "get_time_series_data": get_time_series_data,
    "summarize_trend": summarize_trend,
    "compare_assets": compare_assets,
    "explain_change": explain_change
}


@app.post("/tool/{tool_name}")
def execute_tool(tool_name: str, payload: dict = {}):

    if tool_name not in TOOLS:
        return {
            "error": f"Tool '{tool_name}' not found"
        }

    tool = TOOLS[tool_name]

    if payload:
        result = tool(**payload)
    else:
        result = tool()

    return {
        "tool": tool_name,
        "result": result
    }