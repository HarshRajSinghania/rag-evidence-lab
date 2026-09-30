import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from rag_evidence_lab.cli import main
from rag_evidence_lab.core import inspect
from rag_evidence_lab.report import render_html


class CLITests(unittest.TestCase):
    def test_html_escapes_untrusted_text(self):
        data = {"cases": [{"id": "<script>", "answer": "<img src=x onerror=alert(1)> [s]", "sources": [{"id": "s", "text": "<script>alert(1)</script>"}]}]}
        html = render_html(inspect(data))
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)

    def test_gate_and_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = {"cases": [{"id": "a", "answer": "Refunds within 30 days [s].", "sources": [{"id": "s", "text": "Refunds within 30 days."}]}]}
            inp, base, html = root/'input.json', root/'base.json', root/'report.html'
            inp.write_text(json.dumps(data))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(inp), '--json', str(base), '--html', str(html), '--max-flagged', '0']), 0)
                data['cases'][0]['answer'] = 'Refunds within 90 days [s].'
                inp.write_text(json.dumps(data))
                self.assertEqual(main([str(inp), '--baseline', str(base)]), 1)
                data['cases'][0]['id'] = 'different'
                inp.write_text(json.dumps(data))
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(inp), '--baseline', str(base)]), 2)
            self.assertTrue(html.read_text().startswith('<!doctype html>'))

    def test_bad_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'bad.json'
            p.write_text('not json')
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(p)]), 2)
