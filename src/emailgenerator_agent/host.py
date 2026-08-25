import json
import os

from langchain_azure_ai.agents.hosting import InvocationsHostServer
from starlette.requests import Request

from emailgenerator_agent.agent.graph import email_graph


def parse_email_output(output: dict) -> str:
    """Convert our custom EmailState into the Invocation response."""
    return json.dumps({
        "subject": output.get("subject", ""),
        "body": output.get("body", ""),
        "validation_result": output.get("validation_result", {}),
        "status": output.get("status", ""),
        "missing_parameters": output.get("missing_parameters", []),
    })


class EmailGeneratorHost(InvocationsHostServer):

    @staticmethod
    def _validate_graph_schema(graph):
        # EmailState is intentionally a custom state schema.
        pass

    async def parse_request(self, request: Request):
        data = await request.json()

        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")

        stream = bool(data.get("stream", False))
        message = json.dumps(data)

        return message, stream

    def build_input(self, message: str):
        data = json.loads(message)

        return {
            "tone": data.get("tone", ""),
            "context": data.get("context", ""),
            "data_points": data.get("data_points", []),
        }


def main():
    port = int(os.environ.get("PORT", "8088"))

    EmailGeneratorHost(
        email_graph,
        output_parser=parse_email_output,
    ).run(port=port)


if __name__ == "__main__":
    main()