"""CLI to ask the agent a question.

Usage:
    python -m filings_assistant.agent.cli "What supply-chain risks does AAPL cite?"
"""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask the Filings Assistant a question")
    parser.add_argument("question", help="Natural-language question about ingested filings")
    args = parser.parse_args(argv)

    from filings_assistant.agent.agent import FilingsAgent

    result = FilingsAgent().ask(args.question)
    print("\n=== ANSWER ===")
    print(result.answer)
    if result.citations:
        print("\n=== CITATIONS ===")
        for c in result.citations:
            print(f"  - {c}")
    print(f"\n(steps={result.steps}, tool_calls={len(result.tool_calls)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
