# Stage 02 HQ correction

Verdict: CORRECTED for the Stage 02 integration requirements, not verified accuracy.
Previous head: bf10f277d23bf633013879668f3ad7cadb5786ac.
Branch: stage02/research-agent-dataset. Normal new commit/push only.

## Live inspection

The user confirmed a Platform Project API key in ignored local .env. Authentication
succeeded through composio 0.21.1 / composio-client 1.43.0. Project identity is not
exposed by the tested operations and is not inferred. Operations:
`toolkits.get(slug="composio_search")` and
`tools.get_raw_composio_tools(toolkits=["composio_search"], limit=100)`.
Live schema evidence: data/stage02-correction-live-catalog.json (also the initial
inspection data/stage02-live-catalog.json). Toolkit and selected Tavily action
version: 20260903_00. All four HQ-observed slugs were independently present.
The live toolkit reports NO_AUTH, empty provider fields and required scopes.
This is a dated observation, not a permanent platform guarantee.
Tavily input requires query:string; optional max_results:integer (default 5),
search_depth:basic|advanced (default basic), include_answer/include_images/
include_raw_content:boolean (default false), exclude_domains/include_domains:
array of strings. Only query was sent; live defaults were used.
No Composio coding-agent skill or package installation was needed.

## Bounded smoke and augmentation

One combined, separate run: stage02-composio-augmentation-20260916.
Salesforce (CRM), SendGrid (Marketing), Vercel (Developer/Infra), Xero (Finance).
Salesforce/Vercel/Xero were all-unknown baseline records; SendGrid was the baseline
extraction failure. Two queries per app: developer API/auth/pricing/access, and MCP.
Eight actual tools.execute calls, eight successes, zero failures, 40 distinct
candidate URLs across apps. Metadata includes query, action, version, arguments,
user ID, attempts and sanitized returned response. No request/response secrets.
Normal Stage 02 retrieval selected 15 pages: 9 readable, 6 failed, 7 readable official.
Seven readable pages were actual Composio-returned candidates. Four strict OpenAI
extractions completed, zero failed requests; 27,891 input / 8,300 output tokens.
Three evidence objects survived deterministic acceptance. All four records remain
needs_verification; postflight flags include four low-confidence and two all-unknown.
Salesforce's four pages failed HTTP 403. SendGrid: 4/4 readable; Vercel: 3/3;
Xero: 2/4. Discovery supplied additional readable official URLs for SendGrid,
Vercel and Xero. Separate values changed for SendGrid buildability rationale,
Vercel auth/access, Xero MCP availability; exact before/after is in correction report.
These changes are unverified first-pass candidates; no baseline value was changed.
Raw flags: quote_not_found 19, missing_field_evidence 29, provenance_mismatch 1,
negative_without_explicit_evidence 1, nonofficial_critical_evidence 3.
No human review, accuracy scoring, final insights, or Stage 03 was performed.

## Integrity, validation, reproduction

The full fallback remains byte-identical across all 105 files, including manifest
and freeze inventory; 103 protected entries in freeze.json match. Every file hash
is recorded in data/stage02-correction-report.json. Baseline first-pass SHA256:
d2ed2c442a31671162af0eb7f43d3f40c34eb369503bb7292f24986e83f04fd2.
Baseline freeze SHA256:
c04db0d3e8c9e4b3589264db21622fc9a45233a721e93a466df8e91f21acf799.
Augmentation first-pass SHA256:
f3ac311fa057c8d7139cb25f1162e9ba3bbbf659cc44485d6df2743d31e997cb.
Augmentation freeze SHA256:
ddbcc8bced25d171fa73056b09a225317c73b1839cd7b10478d6d903d04ea525.

Commands with .venv Python: `-B -m unittest discover -s tests -v` (26 passed),
`-B -m agent.stage02_correction_validate` (zero errors, clean credential scan),
`-B -m agent.stage02 verify-freeze --run-id stage02-full-fallback-20260916`,
`-B -m agent.stage02 verify-freeze --run-id stage02-composio-augmentation-20260916`.
Both hash checks pass. `git diff --check` passes; .env is ignored.
The initial sandboxed test attempt could not write temporary files; all tests
passed with filesystem access. Scanner initially matched the substring sk- within
a pre-existing supportdesk CSS filename; adding a token boundary removed that
false positive. No dataset edit or security redaction was necessary.

Run `-B -m agent.stage02_correction` to execute the bounded pipeline with local
credentials. It rejects an existing run directory, never overwrites a frozen run.
For a distinct future run, change RUN explicitly before execution. Existing
checkpoints preserve retrieval text, hashes, extraction, repairs, failures and usage.
Offline validator verifies exact IDs, canonical schema, aggregate/checkpoint parity,
source hashes, freeze hashes, invocation metadata, consumed candidates and secrets.

## Remaining baseline weaknesses and boundary

Original counts stay visible: 19 all-unknown; 13 no usable official source;
100 accepted-record low-confidence; 10 buildability-without-rationale;
349 raw unmatched-quote flags; 9 unsupported-negative flags; SendGrid failure.
Counts overlap and are deterministic flags, not human-confirmed errors. Identity,
repository ownership, rationale, evidence meaning and negative claims need Stage 03.
No Notion state, main branch, merge or Stage 03 work was modified/performed.
The original STAGE02.md is retained as the historical pre-correction execution record.

Frozen run files retain Windows line endings under the existing -text rule. The
whitespace attribute recognizes CR at end of line so staged diff checks preserve
exact frozen bytes rather than rewriting them.
