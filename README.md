# Evidence-backed integration research — Stage 02

Stage 02 starts from accepted Stage 01 commit `74bd9f5d9511be8b3777d0a079f5aaf174992fb2`
on `stage02/research-agent-dataset`. It owns research and initial extraction only.
`agent/schema.py` remains the canonical v1.0 contract. Stage 03 owns semantic verification,
human checking and pattern analysis. No Stage 02 command builds, deploys or reviews the legacy UI.
See `STAGE02.md` for the original fallback run and `STAGE02-CORRECTION.md` for the subsequent successful authenticated Composio correction. The original authentication blocker is resolved; findings remain unverified.
The recorded complete fallback run is `stage02-full-fallback-20260916`.

## Prerequisites and installation

Python 3.10+ (tested locally with 3.14.5), outbound HTTPS and valid Composio/OpenAI keys.
From `U:\composio-research-assessment`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-stage02.txt
```

Create the ignored local `.env` using `.env.example` as a guide:

```text
OPENAI_API_KEY=<populate locally>
OPENAI_MODEL=gpt-4.1-mini-2025-04-14
COMPOSIO_API_KEY=<populate locally>
COMPOSIO_USER_ID=stage02-research
```

Do not paste credentials into chat or commit them. The pipeline automatically loads
plain `KEY=value` entries without executing or interpolating their contents. Existing
process variables take precedence. OpenAI uses strict JSON-schema Structured Outputs
via the official Chat Completions HTTPS endpoint, with the standard-library transport.
For the recorded complete dependency set, install `requirements-stage02-lock.txt`
instead of the two direct requirements (platform compatibility still applies).
The Composio Python SDK is used directly; a CLI or provider plugin is unnecessary.

## Inspect, smoke-test, collect

Inspect the live catalog before choosing an action:

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage02 inspect
```

Read `data/stage02-live-catalog.json`: choose a web-search action, check its actual
input schema and authentication requirements. Pass its exact slug; the pipeline
validates that it exists and pins the toolkit's dated live version. Actions requiring
additional mandatory parameters are rejected until explicitly implemented.

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage02 smoke --action <inspected-action-slug> --run-id stage02-smoke
.\.venv\Scripts\python.exe -B -m agent.stage02 run --action <inspected-action-slug> --run-id stage02-full
```

The smoke test selects Salesforce, Zendesk, Google Ads and Notion. The full run
requires a frozen smoke test with zero extraction failures and some accepted evidence.
If the live catalog/search fails, preserve the exact failure first, then explicitly
activate the seed-document discovery fallback:

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage02 smoke --fallback-seeds --run-id stage02-smoke-fallback
.\.venv\Scripts\python.exe -B -m agent.stage02 run --fallback-seeds --run-id stage02-full-fallback
```

A fallback is an honest limitation, not a Composio success. It does not prove MCP/API
absence. Failed extraction emits a schema-valid unknown record and an explicit failure.
Composio rejection with HTTP 401 requires correcting the local project key.

## Checkpoints and outputs

Rerun the same command and run ID after interruption. Completed per-app checkpoints
are reused without search, retrieval or model calls; incompatible model, prompt,
schema, seed or tool configurations are rejected. A frozen run cannot be resumed
or overwritten; use a new run ID for any new research. One documented security-only
redaction removed Stripe documentation credential examples before publication; original
hashes are retained in `data/stage02-security-redactions.json`, with every research
claim value preserved.

`data/runs/<run_id>/` contains:

- `manifest.json`: input/model/tool/prompt/schema configuration, bounds and actual usage.
- `apps/001.json` through `apps/100.json`: assigned identities, raw extraction,
  accepted record, deterministic repairs, discovery responses, normalized retrieved
  text, requested/final URLs, timestamps, hashes, failures and validation flags.
- `first-pass.json`: frozen accepted records; genuine raw output remains per app.
- `failures.json`: extraction or unexpected app-processing failures.
- `quality-flags.json`: per-app deterministic flags for Stage 03.
- `freeze.json`: SHA-256 hashes of all frozen JSON artifacts.

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage02 verify-freeze --run-id stage02-full
.\.venv\Scripts\python.exe -B -m agent.stage02_audit --run-id stage02-full
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

The audit writes a separate `data/stage02-postflight-<run_id>.json`, without
changing frozen research. It checks schema, exact run identities, source hashes,
aggregate/checkpoint equality, artifact hashes and supplemental verification flags.

`data/stage02-input-lock.json` locks the accepted seed content and identities. The recovered original assessment attachment from HQ contains apps 1–90, all
matching the accepted seeds by ID/name/category; its final category has no rows.
`data/stage02-input-reconciliation.json` records this comparison and the status
of user confirmation for apps 91–100.
Seeded documentation origins are treated as assigned official sources; this trust
needs Stage 03 verification, especially delegated documentation hosts and ambiguous names.

## Bounds and interpretation

Three app workers, two discovery queries per app, at most four retrieved pages,
20-second retrieval and 90-second OpenAI timeouts, one retry for OpenAI/Composio,
14,000 normalized characters per page and 42,000 total evidence characters per app.
Composio's SDK additionally has a 30-second timeout and one internal retry.
OpenAI calls and returned token usage are counted; no cost estimate is invented.

Search snippets are candidates only. Extraction receives actual retrieved text and
must abstain without evidence. Deterministic checks reject missing/failed provenance,
fabricated quotes, mixed unknown enums and unsupported negative claims. A matching
quote proves text grounding, not semantic truth. JavaScript shells can remain readable
but incomplete; auth/access distinctions and buildability still require Stage 03 checking.
No record is automatically human-audited, and no human accuracy score is produced.

## Legacy artifacts

Existing `agent/pipeline.py`, `agent/review.py`, `agent/build.py`, top-level data and
`site/` predate Stage 01 and are preserved. They are not Stage 02 outputs. Do not use
legacy result counts or the deployed presentation as evidence that this new research
run succeeded. `STAGE01.md` documents the accepted baseline and later-stage boundaries.

## Pre-Stage 03 canonical state

Stage 01 and corrected Stage 02 are the governed research baseline. Main also preserves earlier work, including `EXPLAIN.md` and the historical Pages publication at https://udaysuryap.github.io/composio-research-assessment/. That publication uses legacy artifacts and is not the verified submission. Pages publishing is manual until the later presentation/deployment stages; merging research must not republish it automatically.

See `PRE-STAGE03-AUDIT.md` for coverage, checks and outstanding verification risks. Do not use legacy analytics or human worksheets as Stage 03 results.

## Stage 03 preparation and manual verification

Stage 03 starts at canonical `0e4090c69242e0281338f97fc27c3ccd009aa51a` on
`stage03/verification-pattern-analysis`. Run offline from the repository:

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage03 prepare
.\.venv\Scripts\python.exe -B -m agent.stage03 check
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

`data/stage03/sample-manifest.json` predeclares seed 42, two apps per category
and two claims per app (40 claims). `REVIEW.md` presents manageable review items;
`human-review.json` is the machine-readable worksheet. Uday personally checks the
source and reports observed values and judgments. Ownership and product identity
must be confirmed even for seeded official URLs. Reviewer/timestamp fields are blank
until actual review. Inaccessible, ambiguous, outdated and unclear sources are unscored.
The challenge set contains frozen quality flags, hard failures and augmentation
disagreements separately; it is never used to inflate unbiased sample accuracy.

`score(reviews, expected)` compares the same complete paired claims with actual Uday
judgments. Both first-pass and final denominators are identical; null accuracy means
no scored claims. Unit-test review fixtures are synthetic and never enter outputs.
Preparation refuses to overwrite changed human worksheets. After review, ingestion,
corrections and finalization must be completed in a resumed Stage 03 session; the
current command deliberately does not finalize or publish the dataset.

`prepared-results.json/csv` retains all 100 identities and first-pass uncertainty.
It is a pending working dataset, not final verified research. Each correction requires
original/corrected values, reason, evidence, method and timestamp in `correction-log.json`.
No augmentation candidate is automatically promoted. `provisional-patterns.json` is
reproduced from prepared rows, contains no product insights, and must not be used as
final Stage 04 evidence. Free-text API breadth is not guessed into categorical buckets.
`baseline-integrity.json` pins all four frozen manifests; `check` detects frozen tampering
and any prepared change without a corresponding correction. Prior artifacts are immutable.
Final metrics, verified-source coverage, semantic failure modes and approximately five
supported product insights remain pending actual source verification and manual review.

Human review updates preserve `review-items.json` as the blank predeclared definition.
If Uday supplies judgments without an inspection time, `reviewed_at` stays null;
`review_reported_at` records the actual report receipt time and is explicitly labeled.
The scorer accepts either timestamp for a completed actual human report. This does not
assert when Uday visited the page. `check` also reconciles human summary and provisional
counts against recorded judgments and prepared rows.

## Completed Stage 03: checked claims and explicit unresolved coverage

All 40 actual Uday review reports are recorded; five unclear claims are unscored.
The final paired sample is 7/35 first-pass and 35/35 final (+80 percentage points).
These are the same 35 sampled claims. The final judgment was supplied alongside each
proposed correction, not independently re-audited after a delay. This is not a
whole-dataset accuracy measurement or proof of working integrations.

Use `data/stage03/verified-results.json` and `.csv` as the conservative verified-only
view, `claim-verification.json` for coverage, and `patterns.json` plus
`pattern-evidence.json` for reproducible Stage03 summaries and bounded insights.
All 100 identities remain. Checked fields retain their documented values. Unchecked
first-pass claims become explicit unknowns with coverage-abstention log entries rather
than being silently promoted as verified. This leaves 22 partially resolved apps and
78 apps with all seven critical fields unresolved, not 78 confirmed failed apps.
No complete row is marked human_audited. API breadth stays unknown without an
independently supported breadth classification. Category comparisons have sparse
checked coverage and cannot support integration-priority rankings.

The original 100-app first pass remains immutable. `correction-log.json` distinguishes
41 substantive/source-supported updates (including five supporting rationale fields)
from 285 automated coverage abstentions; abstentions are not proven incorrect claims.
`automated-checks.json` and `targeted-source-excerpts.json` record actual follow-up for
SendGrid, Vercel, Xero and HubSpot. Excerpt hashes cover short retained excerpts, not
whole web pages. `prepared-results` is an audit reconstruction and is not the final
active evidence view. No new Composio call was made; Xero retains original Composio
augmentation provenance plus official-domain ownership triangulation.

Reproduce from the repository, keeping human judgments unchanged:

```powershell
.\.venv\Scripts\python.exe -B -m agent.stage03_finalize generate --timestamp 2026-09-16T21:14:49+00:00
.\.venv\Scripts\python.exe -B -m agent.stage03_finalize check
.\.venv\Scripts\python.exe -B -m agent.stage03 check
.\.venv\Scripts\python.exe -B -m agent.stage03_security
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -q
```

Later substantive review requires a new governed checkpoint; do not edit frozen
Stage02 runs or human history to improve displayed numbers. Stage03 is ready for HQ
audit with material coverage limitations. Stage04 may consume these files only after
HQ acceptance and explicit authorization. No presentation, deployment, main merge or
Notion modification is part of this work.
