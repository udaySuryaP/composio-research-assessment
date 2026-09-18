# Composio Assessment

Research and integration-readiness analysis for 100 apps across 10 categories.

[Live assessment](https://udaysuryap.github.io/composio-research-assessment/) · [Download HTML](https://github.com/udaySuryaP/composio-research-assessment/raw/refs/heads/main/submission/composio-assessment-uday.html)

## What it does

A Python pipeline discovers documentation, retrieves source text, extracts structured claims, checks evidence, and records corrections. The report groups apps into build, investigate, and outreach candidates, with a searchable 100-app matrix and inspectable evidence.

Each app captures purpose, authentication, access gates, API type and breadth, MCP availability, documentation-based readiness, and the main blocker. Unknowns remain explicit.

## Verification

- Historical human review: 40 claims across 20 apps; 35 scoreable, five unclear. The first pass matched 7/35 judgments; the corrected projection matched 35/35 on the same claims. These judgments were supplied during correction, not independently re-audited.
- Fresh purposive source review: 60 records across 20 apps; 47 correct, eight needing caveats, five unsupported, zero unverifiable. Six correct records were appropriately unresolved. This was agent source review, not fresh human verification, and was not fully blinded. Additional reviews and corrections are recorded separately.

Neither sample estimates whole-dataset accuracy.

## Outputs

- [`submission/composio-assessment-uday.html`](submission/composio-assessment-uday.html): self-contained report; opens directly and works offline.
- [`data/correction/submission-fixes-20260918/final-corrected-dataset.json`](data/correction/submission-fixes-20260918/final-corrected-dataset.json): current corrected dataset and claim evidence; prior datasets and review outcomes remain preserved.
- [`final-artifact-20260917/patterns.json`](final-artifact-20260917/patterns.json): counts, denominators, candidate lists, and grouping rules.
- [`submission/RELEASE.md`](submission/RELEASE.md): artifact identity and release notes.

## Run locally

Use Python 3.12. From the repository root:

```sh
python -m pip install -r requirements-stage02.txt
python -B final_build.py
python -B -m unittest discover -s tests -v
python -B -m agent.release check
```

The rebuild uses saved inputs and makes no research calls. Open `submission/composio-assessment-uday.html` to view the release, or `final-artifact-20260917/composio-assessment-uday.html` to view the rebuild.

For new research, set `OPENAI_API_KEY` and `COMPOSIO_API_KEY` in your shell or a repository-root `.env` copied from `.env.example`. Optional `OPENAI_MODEL` and `COMPOSIO_USER_ID` configure the existing model and user context. Shell values take precedence; `.env` is ignored and keys must never be committed. No drive-specific setup is required. Inspect `python -m agent.production_research --help` before starting a fresh run; credentials are unnecessary for offline rebuilding and tests.

## Limitations

Research coverage remains partial: 95 source-backed, 803 caveated, and 402 unresolved fields out of 1,300. The submission correction pass resolved 51 missing product purposes; Paygent Connect and iPayX purposes remain unresolved. Readiness is documentation-based; no integrations were executed end to end. API breadth is not an exhaustive action inventory.
