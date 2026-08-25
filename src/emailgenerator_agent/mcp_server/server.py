from fastmcp import FastMCP

from .tools import validate_email_content


mcp = FastMCP(
    name="Professional Email Tools"
)


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


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )