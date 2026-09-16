# Stage 02 execution record

Status: **BLOCKED for authenticated Composio catalog/schema verification**.
The complete fallback 100-app pipeline was executed and frozen. The configured
Composio key, including the user-supplied replacement, received HTTP 401 on all
four live SDK catalog attempts. No search action was selected, no live action
schema was obtained and no Composio search invocation occurred. The public toolkit
catalog was read separately; its documented version is not an observed account version.

Starting commit: `74bd9f5d9511be8b3777d0a079f5aaf174992fb2`.
Branch: `stage02/research-agent-dataset`. Remote main was not used as a baseline.
The tree was clean and Stage 01 HEAD exact before the Stage 02 branch was created.

## Input reconciliation

Exactly 100 unique assigned IDs/names, ten categories with ten apps each. Recovered
HQ attachment `Pasted markdown(8).md` contains IDs 1–90, matching seed ID/name/category
exactly. The user explicitly confirmed IDs 91–100 in this Stage 02 task, including
the spelling `higgsfield`. Original hints are retained in the reconciliation artifact.
No identities were substituted. Paygent Connect still needs identity verification.

## Smoke tests

`stage02-smoke-seeds-20260916`: four apps, four successful OpenAI calls, 14,323 input
and 6,914 output tokens; seven pages, five readable, two failed; six accepted evidence
objects. Validation rejected many fabricated excerpts and claims. Frozen unchanged.

`stage02-smoke-grounded-20260916`: four apps, four successful OpenAI calls, 14,565
input and 5,920 output tokens; seven pages, five readable, two failed; 14 accepted
evidence objects. The prompt was tightened and seed doc URLs removed from model
input. Both smoke runs are actual seed-fallback runs, not Composio successes.

## Full run

Run: `stage02-full-fallback-20260916`.
UTC start: `2026-09-16T17:15:47.182326+00:00`.
UTC end: `2026-09-16T17:26:34.023349+00:00`.
100 accounted for; 99 partial/needs-verification, one failed; zero wholly unflagged.
101 model requests; two failed extraction attempts; 350,669 input and 202,645 output
tokens. SendGrid failed both attempts with ValueError; both returned the configured
6,500-token maximum. Truncation is probable, but the original exception log lacks
finish-reason detail. No failed output was invented or rerun into the frozen snapshot.

136 pages requested; 110 readable, 26 failed; 106 readable pages classified official;
307 accepted evidence objects. Source classification trusts assigned seed origins;
redirected origins are reclassified. Matching text does not prove a claim's meaning.
Zero Composio search calls. Discovery used assigned documentation seeds after the
catalog authentication failure; the fallback was explicitly activated.

Raw-generation flag counts: missing_field_evidence 617; quote_not_found 349;
nonofficial_critical_evidence 24; raw_identity_mismatch 15; no_usable_official_source 13;
low_confidence 12; negative_without_explicit_evidence 9; mixed_unknown_enum 8;
provenance_mismatch 8; unclear_claim_support 2; mixed_none_auth 1.
Counts are overlapping check occurrences, not independently verified errors.

Postflight errors: zero. Supplementary accepted-record flags: low_confidence 100;
all_research_fields_unknown 19; no_usable_official_source 13; nonofficial_critical_evidence 12;
buildability_without_rationale 10; official_repository_ownership_needs_check 2;
missing_field_evidence 1; api_auth_contradiction 1. These remaining weaknesses are
explicit and require Stage 03; frozen first-pass records were not rewritten.

Total across both smokes and full run: 109 OpenAI requests, two failed attempts,
379,557 input and 215,479 output tokens. Billing and cache discounts were not observed,
so no monetary cost is claimed.

## Validation

- `python -B -m unittest discover -s tests -v` under `.venv`: 26 tests passed.
- `python -B -m agent.stage02_audit --run-id stage02-full-fallback-20260916`: 100 records,
  zero integrity errors; exact identity/schema/checkpoint/source/freeze checks passed.
- `python -B -m agent.stage02 verify-freeze --run-id <run_id>`: all three frozen runs passed.
- Live SDK catalog inspection: HTTP 401, documented separately; no action schema invented.

The audit adds deterministic flags outside the frozen run. It is not a semantic audit,
human check or accuracy estimate. No human reviewer identity or accuracy was generated.

## Outputs and boundary

Consume `data/stage02-input-lock.json`, `data/stage02-input-reconciliation.json`,
`data/stage02-composio-inspection.json`, `data/stage02-catalog-failure.json`, both smoke
run directories, the full run directory and its separate `data/stage02-postflight-*.json`.
Each app checkpoint preserves raw extraction, accepted record, repairs, flags, actual
retrieved normalized text, requested/final URLs, timestamps, hashes and failure/usage.
`freeze.json` protects aggregate and per-app bytes; frozen runs reject overwrite.

Secrets remain local in ignored `.env`. Artifact serialization scrubs configured
credential values. No Notion mutation, merge, main change, deployment, substantive
pattern analysis, human audit or Stage 03 execution was performed.

## Documented security-only redaction before publication

GitHub push protection rejected the first unpushed local commit because a retrieved
Stripe documentation page included test-key examples. The examples were redacted
from that source and any raw evidence quotation, and affected content/artifact hashes
were refreshed. All first-pass research claim values were asserted unchanged.
`data/stage02-security-redactions.json` preserves original frozen hashes, before/after
source hashes and the reason; the original unsafe commit was replaced before pushing.
Future retrieval redacts credential patterns before hashing/extraction. This is an
explicit security exception to byte immutability, not a research correction or Stage 03.
