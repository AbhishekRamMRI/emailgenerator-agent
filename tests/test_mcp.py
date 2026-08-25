import pytest
from fastmcp import Client

from emailgenerator_agent.mcp_server.server import mcp


@pytest.mark.asyncio
async def test_validate_email():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "validate_email",
            {
                "subject": "Order Delivery Update",
                "body": (
                    "Dear Customer,\n\n"
                    "We apologize for the delay in your order."
                ),
            },
        )

        assert result.data["valid"] is True
        assert result.data["issues"] == []


@pytest.mark.asyncio
async def test_invalid_email():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "validate_email",
            {
                "subject": "",
                "body": "",
            },
        )

        assert result.data["valid"] is False
        assert len(result.data["issues"]) > 0
