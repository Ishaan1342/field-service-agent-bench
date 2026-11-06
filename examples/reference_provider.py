"""Oracle fixture for checking the promptfoo integration. NOT a model baseline."""
import json
from servicebench.evaluate import load_cases, oracle_answer


def call_api(prompt, options, context):
    case = next(c for c in load_cases() if c["id"] == context["vars"]["case_id"])
    return {"output": json.dumps(oracle_answer(case))}
