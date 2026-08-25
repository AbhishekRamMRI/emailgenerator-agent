import asyncio
import json
from pathlib import Path

from emailgenerator_agent.agent.graph import email_graph


def load_test_cases():
    path = Path(__file__).parent / "test_cases.json"

    with open(path, "r") as file:
        return json.load(file)


async def run_case(case):
    result = await email_graph.ainvoke(case["input"])

    expected = case["expected"]

    checks = []

    # Check status
    checks.append(
        result.get("status") == expected["status"]
    )

    # Check missing parameters
    if "missing_parameters" in expected:
        checks.append(
            set(result.get("missing_parameters", []))
            == set(expected["missing_parameters"])
        )

    # Check generated email
    if expected.get("required_subject"):
        checks.append(
            bool(result.get("subject", "").strip())
        )

    if expected.get("required_body"):
        checks.append(
            bool(result.get("body", "").strip())
        )

    # Check MCP validation
    if expected.get("validation_must_pass"):
        validation = result.get("validation_result", {})

        checks.append(
            validation.get("valid") is True
        )

    passed = all(checks)

    return passed, result


async def main():
    cases = load_test_cases()

    passed_count = 0

    print("\nEmail Generator Evaluation on edge case")
    print("\n")

    for index, case in enumerate(cases, start=1):
        try:
            passed, result = await run_case(case)

            status = "PASS" if passed else "FAIL"

            print(f"\n[{status}] {index}. {case['name']}")

            if passed:
                passed_count += 1
            else:
                print("Result:")
                print(
                    json.dumps(
                        result,
                        indent=2,
                        default=str,
                    )
                )

        except Exception as error:
            print(f"\n[ERROR] {index}. {case['name']}")
            print(f"Error: {error}")

    total = len(cases)

    print("\n" f"Passed: {passed_count}/{total}")

    if passed_count == total:
        print("Evaluation: SUCCESS")
    else:
        print("Evaluation: FAILED")


if __name__ == "__main__":
    asyncio.run(main())