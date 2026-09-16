# Composio Product Intern Assessment

An evidence-grounded research pipeline for 100 assigned app identities across 10 categories, with a deterministic human sample, logged corrections, a conservative verified projection, and a standalone case study.

## Live case study

[Public case study](https://udaysuryap.github.io/composio-research-assessment/) — Stage 05 publication validation is recorded in STAGE05.md. Only the accepted standalone artifact is published; historical presentation is excluded.

## Submission artifact

Upload `submission/composio-assessment-uday.html`: a self-contained 81,369-byte HTML file with inline CSS, JavaScript and all 100 matrix rows. Open it directly in a browser; core content and filtering work offline. Do not zip it. [Repository](https://github.com/udaySuryaP/composio-research-assessment).

## What I built

A Python research agent retrieves source text, extracts structured claims with OpenAI strict JSON schema, checks provenance and evidence grounding, and freezes the first pass. Human verification and targeted source checks are recorded separately. The final case study embeds the accepted verified-only projection.

## Workflow

Assigned apps → discovery → source retrieval → structured extraction → evidence checks → deterministic human verification → corrections → verified projection → case study.

## Composio usage

Initial Composio authentication failed and the complete baseline used assigned seed-document discovery. After correcting the key type to a Composio Platform Project API key, live `composio_search` inspection selected `COMPOSIO_SEARCH_TAVILY`, version `20260903_00`. Eight successful augmentation searches ran in a separate frozen checkpoint. This does not imply all research used Composio. See STAGE02-CORRECTION.md and data/runs/stage02-composio-augmentation-20260916/ for retained provenance. No new research calls were made in Stage 05.

## Verification

Seed 42 predeclared 20 apps and 40 claims. Uday supplied 40 actual human review reports: 35 scoreable, five unclear/unscored, zero pending. On the same 35 claims, first pass matched 7/35 (20%) and final verified judgment matched 35/35 (100%): +80 percentage points. Final judgments were supplied during verification, rather than an independent delayed re-audit. This is a sample-level result and does not measure whole-dataset accuracy.

## Key limitations

Only 44/700 critical claims are independently checked; 656 remain unresolved. There are 22 partially resolved apps, 78 unresolved across all seven critical fields, and zero fully verified app records. API breadth is unknown for all 100. No integrations were executed end-to-end. Five sampled claims remain unresolved. Category ranking and population prevalence are unsupported. The recovered original assignment contains rows 1–90; accepted seeds contain 100 identities. See data/stage02-input-reconciliation.json for the additional-row confirmation record and submission/COMPLIANCE.md for itemized coverage.

Unknown means unresolved, rather than no API, no MCP, or a blocked integration.

## Run locally

Open `submission/composio-assessment-uday.html` in a browser. Windows, Python 3.10+ and Node.js are required only for rebuilding/checking the work, not viewing it.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-stage02.txt
Start-Process .\submission\composio-assessment-uday.html
```

## Reproduce checks

Accepted freeze manifests retain Windows paths; run these checks on Windows (the Pages runner uses Windows too). From a complete Git checkout on `stage05/final-submission`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -B -m agent.stage02 verify-freeze --run-id stage02-full-fallback-20260916
.\.venv\Scripts\python.exe -B -m agent.stage03 check
.\.venv\Scripts\python.exe -B -m agent.stage03_finalize check
.\.venv\Scripts\python.exe -B -m agent.stage04 check
node submission/check-interactions.cjs
.\.venv\Scripts\python.exe -B -m agent.stage05
.\.venv\Scripts\python.exe -B -m agent.stage03_security
git diff --check
```

Checks use retained evidence and require no API keys or fresh research. `agent.stage04 check` deterministically rebuilds the HTML and asserts byte equality. Optional rebuild: `python -B -m agent.stage04 build`. Fresh research instructions, credentials and frozen-run safeguards remain in STAGE02.md / STAGE02-CORRECTION.md; do not overwrite accepted checkpoints.

## Repository structure

- `agent/`: research, schema, verification, projection, submission and hosting checks.
- `data/runs/`: immutable baseline checkpoints and freezes.
- `data/runs/stage02-composio-augmentation-20260916/`: separate Composio augmentation.
- `data/stage03/`: sample definition, actual reviews, corrections, verified rows, claim coverage and bounded patterns.
- `submission/`: final HTML, embedded-JavaScript harness, compliance audit and reviewer notes.
- `tests/`: 53 existing tests.
- `.github/workflows/pages.yml`: manual Pages publication; installs pinned direct dependencies, runs checks, publishes only a byte-identical HTML copy.
- `STAGE01.md`–`STAGE04.md`: historical accepted implementation records; `STAGE05.md`: final preparation record.

## Historical artifact reconciliation

`site/`, root `case-study.html`, EXPLAIN.md and earlier top-level presentation/data are historical outputs, not the final submission. They are preserved for audit history and excluded from deployment. The final output is exclusively `submission/composio-assessment-uday.html`.

STAGE04.md records the implementation handoff's browser limitation. A later independent HQ audit completed Chromium desktop/mobile QA (1440×1000 and 390×844), direct local opening and offline interaction checks, and accepted Stage 04 at `402e90d7f5a33b2dee9f0087e6d8e11a6708e307`. It was subsequently merged into canonical main `cc335e607b8d0a8af4f2715b8a912056bceec274`. The historical handoff remains unchanged. Stage 05 repeats hosted QA; its branch remains separate pending HQ final audit.
