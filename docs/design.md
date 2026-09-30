# Design

`core.py` validates an exported run, splits answers into approximate claims, extracts bracketed source IDs, and compares claim tokens/numeric literals against eligible sources. `cli.py` handles file IO, reporting and gate exit codes. `report.py` escapes text into a portable HTML report.

No model provider is contacted and no judge model is required. The benefit is reproducible, inexpensive triage; the tradeoff is weak semantic understanding. Explicit false-negative tests prevent the README from promising more than the implementation delivers.

Baseline comparison uses per-case flagged claim counts. It refuses mismatched case IDs and thresholds to prevent accidental comparison of different suites. It does not detect every changed failure and does not enforce source/prompt equality.

The included data is synthetic. The current splitter and tokenization are deliberately small, and the stopword list is only a basic English/Spanish aid. Robust sentence parsing, evidence entailment, and language-independent numeric normalization remain separate future work.

Version 1 reports contain a summary and cases with claims, flags, best matching source IDs, overlap, unmatched numbers and full source text. This is an initial schema and may evolve with a documented version change.
