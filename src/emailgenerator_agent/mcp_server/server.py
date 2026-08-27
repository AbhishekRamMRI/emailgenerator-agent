from pathlib import Path

from fastmcp import FastMCP
# from fastmcp.apps import AppConfig

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from ..agent.graph import email_graph
from .tools import validate_email_content


mcp = FastMCP(
    name="Professional Email Tools"
)


# ---------------------------------------------------------
# MCP App UI resource
# ---------------------------------------------------------

UI_PATH = Path(__file__).parent / "ui" / "dist" / "index.html"


@mcp.resource(
        uri="ui://email-generator",
    mime_type="text/html;profile=mcp-app",
)
def email_generator_ui() -> str:
    """
    React MCP App UI.
    """

    return UI_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------
# Generate Email
# ---------------------------------------------------------

@mcp.tool(
    # app=AppConfig(
    #     resource_uri="ui://email-generator",
    #     visibility=["model", "app"],
    # )
    meta={
        "ui": {"resourceUri": "ui://email-generator"}
    }
)
async def generate_email(
    tone: str,
    context: str,
    data_points: list[str],
) -> dict:
    """
    Generate and validate an email using LangGraph.
    """

    result = await email_graph.ainvoke(
        {
            "tone": tone,
            "context": context,
            "data_points": data_points,
        }
    )

    return {
        "subject": result.get("subject", ""),
        "body": result.get("body", ""),
        "status": result.get("status", ""),
        "validation_result": result.get(
            "validation_result",
            {},
        ),
    }

# ---------------------------------------------------------
# Validate Email
# ---------------------------------------------------------

@mcp.tool()
def validate_email(
    subject: str,
    body: str,
) -> dict:
    """
    Validate a generated professional email.

    Returns whether the email passes deterministic
    content validation checks.
    """

    result = validate_email_content(
        subject=subject,
        body=body,
    )

    return result.model_dump()

@mcp.tool()
def approve_email(
    subject: str,
    body: str,
) -> dict:
    """
    Approve and send the generated email.

    This is a demo operation. No real email is sent.
    """

    return {
        "status": "approved",
        "message": "Email has been sent",
        "subject": subject,
    }


@mcp.tool()
def reject_email(
    subject: str,
    body: str,
) -> dict:
    """
    Reject the generated email.

    This is a demo operation.
    """

    return {
        "status": "rejected",
        "message": "Email has been rejected",
    }
# ---------------------------------------------------------
# Server
# ---------------------------------------------------------

if __name__ == "__main__":
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:8080",
                "http://127.0.0.1:8080",
            ],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=[
                "mcp-protocol-version",
                "mcp-session-id",
                "authorization",
                "content-type",
            ],
            expose_headers=["mcp-session-id"],
        )
    ]

    app = mcp.http_app(
        middleware=middleware,
    )

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )