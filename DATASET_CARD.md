# Dataset card

## Purpose

A small public smoke-test dataset for structured, evidence-grounded agent
outputs. It is not a validated industrial troubleshooting benchmark.

## Dataset

Thirty English-language fictional cases across electrical, cooling, pneumatic,
lubrication, instrumentation, compatibility and policy categories. Each includes
a synthetic observation, an applicable fictional manual and a distractor. All
text and labels are specific to this dataset. No private employer or customer
materials were used. The labels have not been validated by field-service experts.
Dataset and code are provided under the repository's MIT license.

## Labels and scoring

Labels specify a controlled diagnosis, authorized disposition, compatible parts
and source coverage. The grader validates exact structured outcomes and verbatim
quotation presence, not semantic entailment. Passing does not establish technical
competence or safety. Missing responses remain in the denominator. Public
promptfoo variables contain case IDs and task context, not expected labels.
The default oracle provider deliberately loads the answer key locally solely to
check the harness; its score is not a model result.

## Limitations and intended development

Manuals name diagnosis codes and the expected dispositions. Cases are relatively
easy and publicly inspectable, so they are unsuitable for held-out leaderboard
claims. No field-service expert validation, industrial safety validation,
statistical representativeness, multilingual evaluation or real-model baseline
has been established. Do not use the cases as repair instructions.

Useful contributions include domain-expert label review, ambiguous cases,
multiple valid answers, more realistic distractors and independently verified
answer-blind baselines. Never add private logs or copyrighted manuals without
permission.
