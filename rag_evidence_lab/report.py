"""Self-contained report; untrusted model/source text is escaped."""
from html import escape


def render_html(report):
    e = lambda value: escape(str(value), quote=True)
    s = report['summary']
    cards = []
    for case in report['cases']:
        rows = []
        for claim in case['claims']:
            flags = claim['flags']
            status = ', '.join(flags) if flags else 'No flags — still verify meaning'
            rows.append(f"<tr><td>{e(claim['text'])}</td><td>{e(', '.join(claim['citations']) or 'None')}</td><td>{e(claim['best_source'] or 'None')}<br>{claim['lexical_overlap']:.0%} lexical overlap</td><td class={'flag' if flags else 'clear'}>{e(status)}</td></tr>")
        sources = ''.join(f"<details><summary>{e(src['id'])}</summary><p>{e(src['text'])}</p></details>" for src in case['sources'])
        cards.append(f"<section><h2>{e(case['id'])}</h2><p>{e(case['question'])}</p><div class=scroll><table><thead><tr><th>Claim</th><th>Citations</th><th>Best match</th><th>Review signals</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><h3>Retrieved sources</h3>{sources}</section>")
    return f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>RAG Evidence Lab report</title>
<style>body{{margin:0;background:#0e1424;color:#e7edf8;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:40px 24px}}h1{{font-size:clamp(28px,5vw,48px);margin:0}}.eyebrow{{color:#86d7cc;letter-spacing:.14em;font-size:13px}}.stats{{display:flex;flex-wrap:wrap;gap:16px;margin:28px 0}}.stats div,section{{background:#182136;border:1px solid #33405b;border-radius:14px;padding:20px}}.stats strong{{font-size:30px;display:block}}section{{margin:22px 0}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #33405b;vertical-align:top;min-width:120px}}td:first-child{{min-width:240px}}.flag{{color:#ffc48b}}.clear{{color:#86d7cc}}details{{margin:8px 0}}summary{{cursor:pointer}}p{{overflow-wrap:anywhere}}.notice{{border-left:3px solid #ffc48b;padding-left:16px;color:#c3ccdf}}</style>
<main><div class=eyebrow>OFFLINE • EXPLAINABLE • NO API KEYS</div><h1>RAG Evidence Lab</h1><p>See which claims need a closer look.</p><div class=stats><div><strong>{s['cases']}</strong>cases</div><div><strong>{s['claims']}</strong>claims</div><div><strong>{s['flagged_claims']}</strong>flagged for review</div></div><p class=notice>{e(report['notice'])} A clean report is not proof of truth. Threshold: {report['threshold']:.0%}.</p>{''.join(cards)}<footer>Generated locally. No external scripts, fonts, or network requests.</footer></main></html>"""
