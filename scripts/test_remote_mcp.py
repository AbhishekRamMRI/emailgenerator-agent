import asyncio

from fastmcp import Client


async def main():
    async with Client("https://emailgenerator-mcp-abhi.azurewebsites.net/mcp") as client:
        tools = await client.list_tools()

        print("\nAvailable MCP tools:")
        for tool in tools:
            print(f"- {tool.name}")

        result = await client.call_tool(
            "validate_email",
            {
                "subject": "Order Delivery Update",
                "body": "Dear Customer,\n\nWe apologize for the delay.",
            },
        )

        print("\nTool result:")
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())