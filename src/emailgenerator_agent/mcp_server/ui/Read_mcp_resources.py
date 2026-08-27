import asyncio

from emailgenerator_agent.mcp_server.server import mcp


async def main():
    resources = await mcp.list_resources()

    print("RESOURCES:")
    for resource in resources:
        print("-", resource.uri)

    print("\nREADING UI RESOURCE...")

    result = await mcp.read_resource(
        "ui://email-generator/app.html"
    )

    html = result.contents[0].content

    print("\nRESOURCE READ SUCCESS")
    print("HTML size:", len(html), "bytes")

    print("\nHas React root:", '<div id="root"></div>' in html)
    print("Has inline script:", "<script>" in html)
    print("Has external JS:", "/assets/" in html)
    print("Has external CSS:", ".css" in html)


asyncio.run(main())
