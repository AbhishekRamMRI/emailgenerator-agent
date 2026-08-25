from pydantic import BaseModel, Field


class EmailValidationResult(BaseModel):
    valid: bool
    issues: list[str] = Field(default_factory=list)


def validate_email_content(subject: str, body: str) -> EmailValidationResult:
    """
    Validate a generated professional email.

    This tool performs deterministic checks only.
    It does not generate or rewrite the email.
    """

    issues: list[str] = []

    if not subject.strip():
        issues.append("Subject is empty.")

    if not body.strip():
        issues.append("Email body is empty.")

    if len(subject) > 150:
        issues.append("Subject is too long.")

    if len(body) < 20:
        issues.append("Email body is too short.")

    return EmailValidationResult(
        valid=len(issues) == 0,
        issues=issues,
    )