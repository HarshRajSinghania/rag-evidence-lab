"""Explainable surface checks for exported RAG runs."""
import re

STOP = set("a an the is are was were be to of in on for and or with as by it this that from can will must not all de del la el los las un una en para por y o con es son se que al como su sus no".split())


def tokens(text):
    return {t for t in re.findall(r"[^\W_]+", text.lower()) if t not in STOP and len(t) > 1}


def numbers(text):
    return set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)*%?(?!\w)", text))


def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("Expected a non-empty 'cases' array")
    ids = set()
    for c in data["cases"]:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not c["id"] or c["id"] in ids:
            raise ValueError("Case IDs must be non-empty unique strings")
        ids.add(c["id"])
        if not isinstance(c.get("answer"), str) or not c["answer"].strip():
            raise ValueError(f"{c['id']}: answer must be non-empty text")
        if not isinstance(c.get("sources"), list):
            raise ValueError(f"{c['id']}: sources must be an array")
        source_ids = set()
        for s in c["sources"]:
            if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not re.fullmatch(r"[\w-]+", s["id"]):
                raise ValueError(f"{c['id']}: source IDs use letters, numbers, underscore or hyphen")
            if s["id"] in source_ids or not isinstance(s.get("text"), str) or not s["text"].strip():
                raise ValueError(f"{c['id']}: duplicate source ID or empty source text")
            source_ids.add(s["id"])
    return data


def inspect_case(case, threshold=0.45):
    sources = {s["id"]: s["text"] for s in case["sources"]}
    # Periods inside numeric values do not split a claim. Bullet/newline boundaries do.
    parts = re.split(r"(?<!\d)[.!?]+\s+|\n+", case["answer"].strip())
    claims = []
    for part in parts:
        if not part.strip():
            continue
        refs = re.findall(r"\[([\w-]+)\]", part)
        text = re.sub(r"\[[\w-]+\]", "", part).strip(" .!?-•")
        if not text:
            continue
        words = tokens(text)
        candidates = [r for r in refs if r in sources] if refs else list(sources)
        matches = []
        for sid in candidates:
            overlap = len(words & tokens(sources[sid])) / len(words) if words else 0.0
            matches.append((overlap, sid))
        best = max(matches, default=(0.0, None))
        evidence = " ".join(sources[r] for r in candidates)
        flags = []
        if not refs:
            flags.append("missing_citation")
        if any(r not in sources for r in refs):
            flags.append("unknown_citation")
        if best[0] < threshold:
            flags.append("low_lexical_overlap")
        absent = sorted(numbers(text) - numbers(evidence))
        if absent:
            flags.append("unmatched_number")
        claims.append({"text": text, "citations": refs, "best_source": best[1],
                       "lexical_overlap": round(best[0], 4), "unmatched_numbers": absent, "flags": flags})
    return {"id": case["id"], "question": case.get("question", ""), "claims": claims,
            "flagged_claims": sum(bool(c["flags"]) for c in claims), "claim_count": len(claims),
            "sources": case["sources"]}


def inspect(data, threshold=0.45):
    validate(data)
    cases = [inspect_case(c, threshold) for c in data["cases"]]
    return {"schema_version": 1, "threshold": threshold,
            "notice": "Heuristic triage only: lexical overlap is not entailment or factuality.",
            "summary": {"cases": len(cases), "claims": sum(c["claim_count"] for c in cases),
                        "flagged_claims": sum(c["flagged_claims"] for c in cases)}, "cases": cases}
