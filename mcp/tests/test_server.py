from mcp.shared.memory import create_connected_server_and_client_session

from springwinter_mcp.server import mcp


async def test_ping_tool_is_exposed_and_callable() -> None:
    async with create_connected_server_and_client_session(mcp) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools.tools] == ["ping"]
        result = await client.call_tool("ping", {})
        assert result.content[0].text == "pong"
