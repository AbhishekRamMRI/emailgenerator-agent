import asyncio

from emailgenerator_agent.agent.graph import email_graph, Context


async def main():
    result = await email_graph.ainvoke(
        {
            "tone": "empathetic",
            "context": "A customer experienced a delay in receiving their order.",
            "data_points": [
                "Order number: 12345",
                "Expected delivery: August 18",
                "Actual delivery: August 20",
                "Compensation: 10% discount",
            ],
        },
        context=Context(user_id="usr-1")
    )

    print("\n" + "=" * 60)
    print("STATUS")
    print("=" * 60)
    print(result.get("status"))

    print("\n" + "=" * 60)
    print("MISSING PARAMETERS")
    print("=" * 60)
    print(result.get("missing_parameters"))

    if result.get("status") == "valid":
        print("\n" + "=" * 60)
        print("SUBJECT")
        print("=" * 60)
        print(result["subject"])

        print("\n" + "=" * 60)
        print("EMAIL")
        print("=" * 60)
        print(result["body"])

        print("\n" + "=" * 60)
        print("MCP VALIDATION")
        print("=" * 60)
        print(result["validation_result"])


if __name__ == "__main__":
    asyncio.run(main())