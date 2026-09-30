# Contributing

Small, reproducible contributions are welcome. This project is early-stage and does not promise semantic factuality assessment.

1. Open or choose an issue describing a concrete input and expected behavior.
2. Fork, create a branch, and implement one focused change.
3. Add a synthetic regression fixture for behavior changes. Never include credentials or customer documents.
4. Run `python -m unittest discover -s tests -v` and the demo command from the README.
5. Open a PR with the problem, resulting behavior, validation, and relevant issue link.

Useful areas: decimal/percentage/unit normalization, multilingual examples, sentence-boundary handling, and RAG exporter recipes. Discuss runtime dependencies or semantic scoring changes first: they change the project's offline, explainable contract.

Be respectful. Critique ideas and code, avoid personal attacks, and assume contributors may be learning. Do not request acceptance, stars, or reviews in unrelated projects.

Development history records actual changes made with AI assistance. Co-authorship should credit people who genuinely contributed; do not fabricate authors or test results.
