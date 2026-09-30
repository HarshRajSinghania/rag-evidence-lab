"""CLI with explicit errors and CI exit codes."""
import argparse
import json
import sys
from pathlib import Path
from .core import inspect
from .report import render_html


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect RAG evidence offline. Heuristic signals, not factuality scores.")
    parser.add_argument("input", type=Path, help="JSON file with a cases array")
    parser.add_argument("--json", type=Path, dest="json_path", help="Write machine-readable report")
    parser.add_argument("--html", type=Path, dest="html_path", help="Write self-contained HTML report")
    parser.add_argument("--baseline", type=Path, help="Compare per-case flagged counts against a previous JSON report")
    parser.add_argument("--threshold", type=float, default=0.45, help="Minimum lexical overlap (0–1)")
    parser.add_argument("--max-flagged", type=int, help="Exit 1 if flagged claims exceed this count")
    args = parser.parse_args(argv)
    if not 0 <= args.threshold <= 1 or (args.max_flagged is not None and args.max_flagged < 0):
        parser.error("threshold must be between 0 and 1; max-flagged must be non-negative")
    try:
        report = inspect(json.loads(args.input.read_text(encoding="utf-8")), args.threshold)
        if args.baseline:
            baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
            if not isinstance(baseline, dict) or baseline.get("schema_version") != 1 or baseline.get("threshold") != args.threshold:
                raise ValueError("Baseline must be a schema_version 1 report with the same threshold")
            old_cases = baseline.get("cases")
            if not isinstance(old_cases, list) or any(not isinstance(c, dict) or not isinstance(c.get("id"), str) or type(c.get("flagged_claims")) is not int for c in old_cases):
                raise ValueError("Invalid baseline case records")
            old = {c["id"]: c["flagged_claims"] for c in old_cases}
            if len(old) != len(old_cases) or set(old) != {c["id"] for c in report["cases"]}:
                raise ValueError("Baseline and candidate must have the same unique case IDs")
            report["regressions"] = [c["id"] for c in report["cases"] if c["flagged_claims"] > old[c["id"]]]
        if args.json_path:
            args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.html_path:
            args.html_path.write_text(render_html(report), encoding="utf-8")
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
    if args.baseline:
        print("Regressed cases: " + (", ".join(report["regressions"]) or "none"))
    return int(bool(report.get("regressions")) or (args.max_flagged is not None and s["flagged_claims"] > args.max_flagged))


if __name__ == "__main__":
    raise SystemExit(main())
