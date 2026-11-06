"""Exact structured-outcome scoring. No LLM judge or network access."""
import json
from pathlib import Path


def load_cases():
    return json.loads((Path(__file__).parent / "cases.json").read_text())


def public_case(case):
    return {k: v for k, v in case.items() if k != "expected"}


def grade(case, answer):
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)
        except (ValueError, TypeError):
            answer = None
    if not isinstance(answer, dict):
        return {"pass": False, "score": 0.0, "reason": "Missing or invalid JSON object", "checks": {}}
    expected = case["expected"]
    checks = {
        "diagnosis": answer.get("diagnosis") == expected["diagnosis"],
        "action": answer.get("action") == expected["action"],
        "compatible_parts": isinstance(answer.get("parts"), list) and
            answer["parts"] == expected["parts"],
    }
    sources = {d["id"]: d["text"] for d in case["context"]}
    evidence = answer.get("evidence")
    valid_sources = set()
    valid_quotes = isinstance(evidence, list) and bool(evidence)
    if isinstance(evidence, list):
        for item in evidence:
            if not isinstance(item, dict):
                valid_quotes = False
                continue
            source, quote = item.get("source_id"), item.get("quote")
            if not isinstance(source, str) or not isinstance(quote, str) or len(quote.strip()) < 8:
                valid_quotes = False
                continue
            if source not in sources or quote not in sources[source]:
                valid_quotes = False
            else:
                valid_sources.add(source)
    checks["verbatim_evidence"] = valid_quotes
    checks["required_sources"] = set(expected["sources"]).issubset(valid_sources)
    score = sum(checks.values()) / len(checks)
    return {"pass": all(checks.values()), "score": score,
            "reason": "; ".join(k for k, passed in checks.items() if not passed) or "All checks passed",
            "checks": checks}


def evaluate(cases, predictions):
    """Missing cases remain in the denominator. Duplicate/unknown IDs are input errors."""
    ids = {c["id"] for c in cases}
    if len(ids) != len(cases):
        raise ValueError("Duplicate dataset IDs")
    answers = {}
    for prediction in predictions:
        if not isinstance(prediction, dict):
            raise ValueError("Prediction must be an object")
        case_id = prediction.get("case_id")
        if not isinstance(case_id, str) or case_id not in ids or case_id in answers:
            raise ValueError("Unknown or duplicate prediction ID")
        answers[case_id] = prediction.get("answer")
    rows = [{"case_id": c["id"], **grade(c, answers.get(c["id"]))} for c in cases]
    total = len(cases)
    passed = sum(r["pass"] for r in rows)
    return {"schema_version": 1, "attempted": total, "provided": len(answers),
            "missing": total - len(answers), "passed": passed, "failed": total - passed,
            "pass_rate": passed / total if total else 0.0,
            "mean_score": sum(r["score"] for r in rows) / total if total else 0.0,
            "results": rows}


def oracle_answer(case):
    """Test-harness canary with access to labels. NOT an agent or model baseline."""
    expected = case["expected"]
    return {"diagnosis": expected["diagnosis"], "action": expected["action"],
            "parts": expected["parts"],
            "evidence": [{"source_id": d["id"], "quote": d["text"]}
                         for d in case["context"] if d["id"] in expected["sources"]]}
