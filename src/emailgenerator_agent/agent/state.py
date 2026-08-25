from typing import TypedDict


class EmailState(TypedDict, total=False):
    tone: str
    context: str
    data_points: list[str]

    prompt: str

    subject: str
    body: str

    validation_result: dict

    status: str
    missing_parameters: list[str]

    retry_count: int