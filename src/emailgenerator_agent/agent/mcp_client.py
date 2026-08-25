import os

from dotenv import load_dotenv
from fastmcp import Client

load_dotenv()

MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]


async def validate_email_with_mcp(
    subject: str,
    body: str,
) -> dict:
    """Call the remote FastMCP email validation tool."""

    async with Client(MCP_SERVER_URL) as client:
        result = await client.call_tool(
            "validate_email",
            {
                "subject": subject,
                "body": body,
            },
        )

        return result.data