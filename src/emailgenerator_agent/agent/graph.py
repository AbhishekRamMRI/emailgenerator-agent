import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from langgraph.types import RetryPolicy
from langgraph.runtime import Runtime
from typing import TypedDict

from .prompts import EMAIL_GENERATOR_PROMPT
from .state import EmailState
from ..mcp_server.tools import validate_email_content


load_dotenv()


class EmailDraft(BaseModel):
    subject: str = Field(description="Professional email subject")
    body: str = Field(description="Professional email body")


llm = ChatOpenAI(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
    temperature=0.7,
)

structured_llm = llm.with_structured_output(EmailDraft)

class Context(TypedDict):
    user_id: str


def build_prompt(state: EmailState) -> EmailState:
    prompt = EMAIL_GENERATOR_PROMPT.format(
        tone=state["tone"],
        context=state["context"],
        data_points="\n".join(
            f"- {point}" for point in state["data_points"]
        ),
    )

    return {
        "prompt": prompt
    }


def generate_email(state: EmailState) -> EmailState:

    prompt = state["prompt"]

    validation_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)

    if validation_result and not validation_result.get("valid", True):

        issues = validation_result.get("issues", [])

        prompt += f"""

The previous email failed validation.

Validation issues:
{chr(10).join(f"- {issue}" for issue in issues)}

Generate a corrected email that fixes these issues.
"""

    result: EmailDraft = structured_llm.invoke(prompt)
    # result: EmailDraft = EmailDraft(subject="gcjdhjkh hcjs hh kjkcjslkj l hcdjkl. hochdj j cdsoho cds", body="gyudccehjhjhnnnnnkljjcdejjjjcdj bhgduhw. udhweu uudywuqyi iuh dwhuihu iu huhuwihiudh iuhuihuidwhiu uhudh. chsdjiojioc ciosjiojciosjojojcojsojcjksjkkckjskks")

    return {
        "subject": result.subject,
        "body": result.body,
        "retry_count": retry_count + 1,
    }


def build_graph():
    graph = StateGraph(EmailState, context_schema=Context)

    graph.set_node_defaults(retry_policy=RetryPolicy(max_attempts=3))
    graph.add_node("validate_inputs", validate_inputs)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("generate_email", generate_email)
    graph.add_node("validate_email", validate_email)

    graph.add_edge(START, "validate_inputs")
    graph.add_conditional_edges(
        "validate_inputs",
        lambda state: (
            "build_prompt"
            if state["status"] == "valid"
            else "END"
        ),
        {
            "build_prompt": "build_prompt",
            "END": END,
        },
    )

    graph.add_edge("build_prompt", "generate_email")
    graph.add_edge("generate_email", "validate_email")
    graph.add_conditional_edges(
        "validate_email",
        route_after_validation,
        {
            "end": END,
            "regenerate": "generate_email",
        },
    )

    return graph.compile()

def validate_inputs(state: EmailState) -> EmailState:
    missing = []

    if not state.get("tone", "").strip():
        missing.append("tone")

    if not state.get("context", "").strip():
        missing.append("context")

    if not state.get("data_points"):
        missing.append("data_points")

    if missing:
        return {
            "status": "missing_input",
            "missing_parameters": missing,
        }

    return {
        "status": "valid",
        "missing_parameters": [],
        "retry_count": 0,
    }

def validate_email(state: EmailState) -> EmailState:
    result = validate_email_content(
        subject=state["subject"],
        body=state["body"],
    )

    return {
        "validation_result": result.model_dump(),
    }

MAX_RETRIES = 3

def route_after_validation(state: EmailState, runtime: Runtime[Context]):
    validation = state.get("validation_result", {})

    # print("Loggin runtime:", runtime.execution_info.node_attempt)

    if validation.get("valid", False):
        return "end"

    if state.get("retry_count", 0) >= MAX_RETRIES:
    # if runtime.execution_info.node_attempt >= MAX_RETRIES:
        return "end"

    return "regenerate"

email_graph = build_graph()