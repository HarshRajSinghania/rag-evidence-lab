"""CLI with explicit errors and CI exit codes."""
import argparse
import json
import sys
from pathlib import Path
from .core import inspect


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect RAG evidence offline. Heuristic signals, not factuality scores.")
    parser.add_argument("input", type=Path, help="JSON file with a cases array")
    parser.add_argument("--json", type=Path, dest="json_path", help="Write machine-readable report")
    parser.add_argument("--threshold", type=float, default=0.45, help="Minimum lexical overlap (0–1)")
    parser.add_argument("--max-flagged", type=int, help="Exit 1 if flagged claims exceed this count")
    args = parser.parse_args(argv)
    if not 0 <= args.threshold <= 1 or (args.max_flagged is not None and args.max_flagged < 0):
        parser.error("threshold must be between 0 and 1; max-flagged must be non-negative")
    try:
        report = inspect(json.loads(args.input.read_text(encoding="utf-8")), args.threshold)
        if args.json_path:
            args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    s = report["summary"]
    print(f"{s['cases']} cases · {s['claims']} claims · {s['flagged_claims']} flagged for review")
    for case in report["cases"]:
        for claim in case["claims"]:
            if claim["flags"]:
                print(f"  {case['id']}: {', '.join(claim['flags'])} — {claim['text']}")
    print(report["notice"])
    return int(args.max_flagged is not None and s["flagged_claims"] > args.max_flagged)


if __name__ == "__main__":
    raise SystemExit(main())
