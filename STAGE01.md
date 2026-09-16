# Stage 01 baseline, requirements and architecture

Baseline locked; Stage 02 execution is not authorized by this document.
Inspected 2026-09-16: main, 91faa5c8fb76680b37d82956ae14b1ee0456b461,
clean working tree. Origin: https://github.com/udaySuryaP/composio-research-assessment.git.
Stage branch: stage01/baseline-architecture. No push or deployment.

## Requirements and existing work

The Stage 01 prompt is available; the original assessment brief is not separately
attached. These requirements use its summary. HQ must reconcile the original brief
and app list before accepting final coverage. The repo already contains a stdlib
Python pipeline, optional AI/Composio adapter, review rules, 100 input/output rows,
human worksheet, static report, portable HTML, five tests and Pages workflow.
All predate Stage 01 and are preserved, not certified here. No package.json,
database or mandatory Python dependencies exist. Local Python: 3.14.5;
supported baseline: Python 3.10+, prefer 3.12 for research runs.

Acceptance criteria: exact assigned 100 identities/categories; description, auth,
self-serve/gated access, API types/breadth, MCP, feasibility/blocker and field evidence;
bounded agent/script execution rather than 100 manual investigations; official docs
first; honest failed retrievals/unknowns; immutable first pass, verified output and
field diffs; meaningful verification and attributed human sample; computed patterns;
self-explanatory single HTML case study/slideshow; later verified live deployment,
source repo and reproducible README; Uday can explain it; no secrets in Git/client UI.
Composio is encouraged, not mandatory. Accuracy/transparency are quality gates.

## Locked architecture

Seeds -> discovery + official retrieval -> strict LLM extraction -> evidence checks
-> targeted second pass -> human audit -> JSON/CSV analysis -> static HTML.

Python with existing HTML/CSS/JS; no database, Next.js migration or agent framework.
Research finds/fetches sources; extraction reads collected evidence only; verification
challenges claims; humans independently audit; analysis counts actual accepted records;
presentation reads outputs. Reuse retrieval/cache/timeouts/checkpoints later, but do
not run or migrate data in Stage 01. Stage 02 emits data/runs/<run_id>/, preserving
legacy artifacts. Log model/prompt/schema versions, token usage, failures and hashes.
First pass must be real extraction, not a keyword baseline relabelled as LLM output.

## Current Composio decision (2026-09-16)

Python composio==0.21.1, current stable PyPI release. Sessions are the current default
for agents dynamically choosing tools; supported direct SDK execution is smaller for
this known-tool batch. No provider plugin needed. COMPOSIO_API_KEY authenticates the
project; stable COMPOSIO_USER_ID scopes calls. composio_search offers web discovery
without separate app connections/search-provider keys. Plan COMPOSIO_SEARCH_TAVILY;
Stage 02 first retrieves its live input schema and dated toolkit version, pins that
version and records it. Never guess parameters or treat search snippets as evidence:
fetch discovered official pages. This fills actual source gaps, not cosmetic SDK use.
No browser toolkit required; JS-only failures remain unknown pending targeted retrieval.
MCP is available via sessions but not planned: extra transport adds no batch value.
Existing DuckDuckGo adapter/version are preserved, not certified. No live call or install
in Stage 01. CLI is absent; installation/login requires approval and is unnecessary
for this SDK baseline. No SaaS connections or Notion writes.

References:
- https://pypi.org/project/composio/ (0.21.1, released 2026-09-04)
- https://docs.composio.dev/docs/quickstart
- https://docs.composio.dev/docs/tools-direct/executing-tools
- https://docs.composio.dev/kb/guide/toolkits-tavily

## Model and contract

OpenAI gpt-4.1-mini-2025-04-14 for extraction/targeted critique. Plan strict json_schema
Structured Outputs with agent.schema.RESEARCH_SCHEMA, replacing legacy json_object
mode in Stage 02. Retain urllib transport; no framework. Handle refusals/truncation,
local validation and retryable failures. Documents are untrusted data, not instructions.
Bound context/concurrency/retries/spend; record usage. On unavailable model, retry only
transient failures then checkpoint unknown/failure. Never silently substitute rules or
claim autonomous model research. Keyword baseline remains a labelled comparator.

References:
- https://developers.openai.com/api/docs/models/gpt-4.1-mini
- https://developers.openai.com/api/docs/guides/structured-outputs

Canonical v1.0 schema is agent/schema.py: all fields required, no extra properties.
Identity/category/website come from reconciled seeds. Unknown lists use ['unknown'];
do not mix unknown/none with known values. Unknown text uses 'unknown'. API breadth
describes retrieved scope, not an invented endpoint census. Confidence is evidence
quality, not accuracy: high = current official support/no conflicts; medium = partial
official coverage; low = weak/indirect/conflicting support; unknown = insufficient.
Verified means passed defined checks, not production functionality. Human-audited
requires a linked attributed audit record.

## Evidence and verification

Evidence attributes each claim to a field with original/final URL, official/community/
third-party status, UTC retrieval time, text SHA-256, exact quote and supports_claim
yes/no/unclear. Link feasibility rationale to underlying auth/access/API evidence.
Stage 02 validates HTTP(S) URLs, resolved domains, timestamps and hashes locally;
schema strings alone do not establish valid URLs or real citations. Official docs,
access and plan pages first; official repositories for official MCP, community repos
only for community MCP; third-party evidence is a flagged fallback. Failed fetches,
missing docs/search results never establish absence. Negative claims require explicit
current support. Quote match establishes text grounding, not semantic correctness.

Automated checks: schema, unique seed IDs, missing/invalid citations, failed source,
non-official critical evidence, unsupported/multiple claims, conflicting sources,
unknowns/low confidence, overbroad API scope, inconsistent auth/access and feasibility
without rationale. Check product identity and freshness. Second pass retrieves missing
sources and critiques flagged fields using evidence only. One bounded repair pass,
then abstain/escalate. Preserve old/new values, reasons, source changes and timestamps.
Model agreement is not independent truth.

Human audit: seed 42 selects two apps per category before examining results. Supplement
with labelled risk cases; never replace random picks. Uday checks auth/access/feasibility
on identical frozen first/final records against live official sources. Store reviewer,
date, URL, expected value, notes and true/false first/final correctness. Unknown or
inaccessible checks stay unscored and separately reported. Deduplicate app/field pairs;
AI is not human. Report first_correct/scored_fields and final_correct/scored_fields
on the same paired sample, counts and uncertainty; no population accuracy claim.
Stage 01 produces no human scores or accuracy percentages.

## Environment and stage boundaries

OPENAI_API_KEY required for model mode; COMPOSIO_API_KEY for SDK discovery.
OPENAI_MODEL and COMPOSIO_USER_ID are nonsecret config. .env.example documents names;
.env and .env.* are ignored. Populate locally and export into the process: the existing
script does not auto-load .env. Never paste keys in chat. Offline tests/report reading
need no keys. No Vercel credential is required in Stage 01.

Stage 02: reconcile original brief/app identities; install pinned optional SDK with
approval; live search schema/version and strict extraction smoke test on 3-5 apps in
an isolated run; wire discovery/retrieval/extraction to canonical contract; implement
local validators, provenance, bounded retry/spend and immutable snapshots; then execute
authorized 100-app generation. Do not build final UI or claim accuracy.
Stage 03: semantic checks, evidence repairs, attributed human sample, paired accuracy
and computed patterns. Stage 04: adapt existing HTML to verified records/evidence.
Stage 05: README/run reproduction, final submission audit and verified live deployment,
target chosen by HQ. Existing Pages workflow must not be triggered by Stage 01.

Architecture is realistic by preserving the stack. Risks: keys/quotas, JS-only docs,
identity ambiguity, strict-contract migration and time for real human audit. Reduce
scope with honest unknowns and a defensible sample, not production integrations,
database or UI rewrite. Only HQ may modify canonical Notion state.

## Stage 01 offline checks

Python 3.14.5: initial 5 integrity tests passed; final 8 tests passed (including
three canonical-contract tests). All 7 Python files parsed successfully with ast.
Pipeline --help succeeded without collection. git diff --check passed; Git warned
only about configured LF/CRLF normalization. .env, .env.local, .venv contents and
data/raw contents are ignored; only .env.example is tracked among .env files.
No SDK install, API smoke test, collection, analytics regeneration, UI build, push,
deployment or Notion mutation. Contract tests are not full runtime schema validation;
local cross-field/URL/source/semantic validation is explicitly Stage 02/03 work.
