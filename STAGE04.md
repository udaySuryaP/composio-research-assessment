# Stage04 — Standalone case-study artifact

Starting commit: a94cce23a4fbdaf9e8b80c03fa8e482f9057f73f
Branch: stage04/case-study-submission

Primary file: submission/composio-assessment-uday.html. Open directly in a browser;
CSS, matrix data and JavaScript are inline. No network or build is required.

Rebuild: python -B -m agent.stage04 build
Validate: python -B -m agent.stage04 check
Full suite: python -B -m unittest discover -s tests -q
Interaction logic: node submission/check-interactions.cjs
Accepted projection: python -B -m agent.stage03_finalize check
Credential scan: python -B -m agent.stage03_security

The matrix is the accepted Stage03 verified-only projection. Unknown is unresolved,
not blocked. Critical coverage follows agent.stage03.FIELDS, including API breadth;
primary blocker is displayed separately. The sample result is paired and supplied
during source verification, not an independent later re-audit.

Validation: all 53 tests pass (49 existing unchanged, four Stage04 tests).
The JavaScript interaction harness tests the actual embedded code using a minimal
DOM stub: search, casing, no matches, all categories, coverage, combined filters,
reset and status count. This is not a browser rendering test.

Browser inspection was attempted. Edge is unavailable and the available in-app
browser rejects file:// URLs by policy. Desktop/mobile rendering and actual local
browser opening remain unconfirmed. Responsive CSS and horizontally scrollable
tables are implemented; manual desktop/mobile QA remains for Stage05.

No deployment or preview was created. Historical site and accepted Stage01–03 files
remain untouched. Stage05 remains responsible for final deployment, README
reconciliation, submission QA and final audit. No Notion changes were made.
