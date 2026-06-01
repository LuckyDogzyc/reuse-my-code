from __future__ import annotations

import json
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.anyio
async def test_mcp_stdio_server_lists_and_calls_reuse_bundle():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "reuse_my_code.mcp_server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert "reuse_bundle" in tool_names
            assert "reuse_verify" in tool_names

            result = await session.call_tool(
                "reuse_bundle",
                {
                    "goal": "给我的 FastAPI 项目加一个安全文件上传功能",
                    "language": "python",
                    "framework": "fastapi",
                },
            )
            assert not result.isError
            payload = json.loads(result.content[0].text)
            matched_assets = {
                item["selected"]["asset_id"]
                for item in payload["results"]
                if item.get("selected")
            }
            assert "fastapi-safe-file-validation" in matched_assets
