import json
import subprocess
import urllib.request

from azure.identity import DefaultAzureCredential


def get_azd_value(name: str) -> str:
    result = subprocess.run(
        ["azd", "env", "get-value", name],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main():
    endpoint = get_azd_value(
        "AGENT_EMAILGENERATOR_AGENT_INVOCATIONS_ENDPOINT"
    )

    payload = {
            "tone": "assertive",
            "context": "Informing the development team that the project deadline must be met without further delays.",
            "data_points": [
                "Project: AI Email Generator",
                "Deadline: 30/August/2026",
                "All pending tasks must be completed before the deadline",
                "Team members must report blockers immediately",
                "No further deadline extensions are planned"
            ]
        }

    credential = DefaultAzureCredential()
    token = credential.get_token("https://ai.azure.com/.default")

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}",
        },
        method="POST",
    )

    print()
    print("=" * 70)
    print("              EMAIL GENERATOR AGENT")
    print("=" * 70)
    print()
    print("Generating email...")
    print()

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    # The Foundry response contains our graph output as a JSON string.
    agent_response = json.loads(result["response"])

    subject = agent_response.get("subject", "")
    body = agent_response.get("body", "")
    validation = agent_response.get("validation_result", {})
    status = agent_response.get("status", "")
    missing = agent_response.get("missing_parameters", [])

    print("-" * 70)
    print("GENERATED EMAIL")
    print("-" * 70)
    print()
    print(f"Subject: {subject}")
    print()
    print(body)
    print()

    print("-" * 70)
    print("MCP VALIDATION")
    print("-" * 70)
    print()
    print(f"Valid : {validation.get('valid')}")
    print(f"Issues: {validation.get('issues', [])}")
    print()
    print(f"Agent status: {status}")

    if missing:
        print(f"Missing parameters: {missing}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
