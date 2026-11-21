# AI Agent Reliability Scorecard

Evaluate an AI agent before trusting it with real work. Score evidence from structured tests, not demos or impressions.

## Agent definition
- Agent / model:
- Vendor and version:
- Task scope (what it may do):
- Environment (accounts, tools, data it can reach):
- Reviewer:
- Date:

## Reliability scorecard
Score 1-5 and record evidence, not impressions.

| Capability | Weight | Test / exercise | Evidence observed | Score |
|---|---:|---|---|---:|
| Task completion | | | | |
| Instruction following | | | | |
| Factual grounding | | | | |
| Tool use accuracy | | | | |
| Error handling / recovery | | | | |
| Consistency across runs | | | | |
| Permission and data discipline | | | | |

Weighted score = sum(score x weight) / sum(weights). Use the score as one input, not an automatic decision.

## Structured tests
1. Give it a routine task with a known correct result. Did it land?
2. Give the same task three times. Were the results consistent?
3. Give a task with a missing input. Did it ask, or guess silently?
4. Give a task slightly outside its scope. Did it stop or proceed anyway?
5. Introduce a deliberate error mid-task. Did it detect, report and recover?

## Failure record
- Incident:
- Trigger / input:
- Impact:
- Detected by agent or by reviewer:
- Recurrence risk:
- Mitigation:

## Calibration
- Strong evidence:
- Missing evidence:
- Follow-up tests needed:
- Over-trust risk to check:
- Reviewer disagreement:

## Decision record
- Recommendation: Trust for scope / Trust with review / Retest / Do not use
- Evidence supporting decision:
- Limits and safeguards required:
- Retest date:
- Approver:
- Date:

## License
Personal and internal business use only. No resale or redistribution.
