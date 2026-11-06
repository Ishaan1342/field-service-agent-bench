import argparse
import json
from pathlib import Path
from .evaluate import evaluate, load_cases, oracle_answer, public_case


def main():
    parser = argparse.ArgumentParser(
        description="Synthetic, non-operational field-service evaluations"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--output", type=Path)
    run = sub.add_parser("evaluate")
    run.add_argument("predictions", type=Path)
    run.add_argument("--output", type=Path)
    export = sub.add_parser("export-promptfoo")
    export.add_argument("--output", type=Path, default=Path("promptfooconfig.json"))
    args = parser.parse_args()
    cases = load_cases()
    if args.command == "demo":
        oracle = evaluate(
            cases, [{"case_id": c["id"], "answer": oracle_answer(c)} for c in cases]
        )
        missing = evaluate(cases, [])
        forged = []
        for case in cases:
            answer = oracle_answer(case)
            answer["evidence"][0]["quote"] = "This unsupported quote is fabricated."
            forged.append({"case_id": case["id"], "answer": answer})
        report = {
            "label": "HARNESS SELF-CHECK ONLY: oracle sees hidden labels, no model evaluated",
            "oracle_canary": oracle,
            "missing_predictions_control": missing,
            "fabricated_evidence_control": evaluate(cases, forged),
        }
        success = (
            oracle["passed"] == len(cases)
            and missing["passed"] == 0
            and report["fabricated_evidence_control"]["passed"] == 0
        )
    elif args.command == "evaluate":
        try:
            predictions = json.loads(args.predictions.read_text())
            if not isinstance(predictions, list):
                raise ValueError("Predictions must be a JSON array")
            report = evaluate(cases, predictions)
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        success = report["failed"] == 0
    else:
        report = {
            "description": "Synthetic field-service harness; default provider is an oracle canary, not a model",
            "prompts": [
                "Return JSON with diagnosis, action, parts, and evidence [{source_id, quote}]. Task: {{task}}"
            ],
            "providers": ["file://examples/reference_provider.py"],
            "tests": [
                {
                    "description": c["id"],
                    "vars": {"task": json.dumps(public_case(c)), "case_id": c["id"]},
                    "assert": [
                        {"type": "python", "value": "file://examples/assertion.py"}
                    ],
                }
                for c in cases
            ],
        }
        success = True
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
