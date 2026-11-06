from servicebench.evaluate import grade, load_cases


def get_assert(output, context):
    case_id = context["vars"]["case_id"]
    case = next(c for c in load_cases() if c["id"] == case_id)
    return grade(case, output)
