"""Quick CLI tester for the runbook RetrievalQA.

Usage:
    export OPENAI_API_KEY="your-key"
    python test_runbook_qa.py "lead volume dropped for website forms"
"""

import sys

from app.services import suggest_runbook_section


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python test_runbook_qa.py 'your incident description'")
        raise SystemExit(1)

    query = " ".join(sys.argv[1:])
    result = suggest_runbook_section(query)

    backend = result.get("backend", "unknown")
    print(f"Backend: {backend}")

    if backend == "langchain_retrievalqa":
        print("\n=== Answer ===\n")
        print(result.get("answer", "<no answer>"))
    else:
        print("\n=== Section ===\n")
        print(result.get("section", "<no section>"))
        print("\n=== Excerpt ===\n")
        print(result.get("excerpt", "<no excerpt>"))

    if "langchain_error" in result:
        print("\n[LangChain error]", result["langchain_error"])


if __name__ == "__main__":
    main()
