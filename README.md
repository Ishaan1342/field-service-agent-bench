# Field Service Agent Bench

> **Early MVP · MIT · Python 3.11+**. Scope and integration limits are documented below.

## Install from this repository

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md) and the
[Changelog](CHANGELOG.md). GitHub CI results, once available, are separate from
local test results.


Thirty **synthetic, non-operational** evidence-grounded troubleshooting cases.
No Atlas Copco material, customer records, private logs or real service manuals.
The seven categories cover electrical, cooling, pneumatic, lubrication,
instrumentation, compatibility and authorization decisions.

## What it measures

Given an observation log, a fictional applicable manual and a distractor for a
different unit, return a JSON object:

```json
{
  "diagnosis": "CONTROL_FUSE",
  "action": "fix_on_site",
  "parts": ["FUSE-24-2A"],
  "evidence": [
    {"source_id": "log", "quote": "an exact quotation from the supplied log"},
    {"source_id": "manual", "quote": "an exact quotation from the supplied manual"}
  ]
}
```

The grader checks the controlled diagnosis label, authorized disposition,
compatible parts, verbatim quotation validity and required source coverage.
All five must pass for a case to pass. Partial scores are diagnostic, not release
approval. Missing/invalid answers score zero and stay in the denominator.
Duplicate/unknown prediction IDs are input errors. This is exact structured
scoring, not a semantic judge of arbitrary free-form reasoning. An exact quote
can still be irrelevant; the current grader checks presence, not entailment.

## Run without any model or API key

```sh
python -m servicebench demo --output artifacts/demo.json
python -m unittest discover -s tests -v
```

**The oracle canary sees the answer labels. Its 30/30 result checks the harness,
not model capability.** The same demo proves missing predictions and fabricated
evidence fail. The dataset is a starter smoke-test suite, not expert-validated
industrial guidance or a held-out leaderboard. Do not use it to perform repairs.

## Evaluate your own outputs

Create a JSON array of `{case_id,answer}` records (FS-001 through FS-030):

```sh
python -m servicebench evaluate predictions.json --output artifacts/results.json
```

Exit 0 means all cases passed, 1 means evaluated failures, 2 means invalid input.
`servicebench.evaluate.public_case` strips expected labels before presenting a
task to a model. The checked-in `cases.json` intentionally contains labels for
local grading; never include those labels in an agent's model prompt.

## Use with promptfoo

```sh
python -m servicebench export-promptfoo --output promptfooconfig.json
PYTHONPATH=. PROMPTFOO_DISABLE_TELEMETRY=1 npx promptfoo@0.125.1 eval -c promptfooconfig.json --no-cache
```

The generated configuration uses promptfoo's Python provider and assertion
interfaces. **Its default provider is also the label-aware oracle**, so the
configuration runs without paid APIs. Replace only the provider with your own
agent for a real evaluation, forwarding the rendered task prompt. Grading labels are loaded by the assertion
from the local dataset, not included in provider variables. The reference
provider deliberately reads labels from that dataset; it remains an oracle.
Re-export after editing cases.
The exact promptfoo version used for local integration verification is recorded
in the build report; install that version for reproduction.

## Contribution roadmap

Expert-review the synthetic labels; add fault ambiguity, multiple valid plans,
genuinely conflicting sources, localization, and answer-blind model baselines.
Use [promptfoo](https://github.com/promptfoo/promptfoo) as the evaluation runner
rather than building another orchestration framework. This is an independent
dataset/grader project, not a change to promptfoo itself.
