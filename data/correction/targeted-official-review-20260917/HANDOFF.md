# Targeted official-source correction handoff

**Status: VERIFICATION-READY**. Ready for fresh independent verification of this evidence-disposed dataset; dataset-wide factual accuracy remains unmeasured.

Branch: `correction/research-coverage`. HEAD/base: `83bd643b087da28d2e1ed1439e381b3a8a9bca7f`. Tracked diff is empty; correction work is local, untracked and uncommitted. Canonical main is clean at the same base. Exact working tree is in HANDOFF.json.

## Scope and provenance

The API-backed continuation remains frozen at 96 extraction / 93 atom review / 84 valid field review apps. No API calls, API-key loads, model/provider changes, credits purchased, quota retries or full-100 restart occurred. All 16 incomplete app reviews now have field-by-field targeted source dispositions; 12 gained corrections, four remain unresolved. Datadog and PitchBook were additionally reviewed because all critical fields were unresolved. Targeted agent research is not fresh human verification.

The final dataset contains 100 apps / 1,300 field dispositions. 117 unresolved fields were completed across 14 apps:
- 36 Klaviyo: purpose, auth_methods, api_available, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 41 Shopify: auth_methods, api_available, api_types, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 43 BigCommerce: auth_methods, api_available, api_types, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 44 Salesforce Commerce Cloud: api_available, access_model, api_breadth, primary_blocker, buildability, buildability_rationale
- 49 Amazon Selling Partner: auth_methods, api_available, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 60 Clay: auth_methods, api_available, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 61 GitHub: api_types, api_available, api_breadth, access_model, primary_blocker, buildability, buildability_rationale, mcp_available, mcp_provider, mcp_ownership, mcp_notes
- 68 MongoDB Atlas: auth_methods, api_available, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 69 Datadog: api_available, api_breadth, primary_blocker, buildability, buildability_rationale
- 73 Linear: auth_methods, api_available, api_types, api_breadth, access_model, buildability, buildability_rationale, mcp_available, mcp_provider, mcp_ownership, mcp_notes
- 76 Monday.com: auth_methods, api_available, api_types, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 81 Stripe: auth_methods, api_available, access_model, primary_blocker, buildability, buildability_rationale, mcp_available, mcp_provider, mcp_ownership, mcp_notes
- 90 PitchBook: auth_methods, api_available, api_types, api_breadth, access_model, primary_blocker, buildability, buildability_rationale
- 99 YouTube Transcript: purpose, auth_methods, api_available, api_types, api_breadth, access_model, primary_blocker, buildability, buildability_rationale, mcp_available, mcp_provider, mcp_ownership, mcp_notes

Corrections only entered unresolved fields. Existing final deterministic QA rejected nine atoms and narrowed ten projected values; no source-integrity field downgrades occurred. Changes are inspectable in deterministic-qa-changes.json. No unrelated valid automated finding was replaced.

Separate provenance artifacts: gap-inventory.json, field-corrections.json, manual-evidence-capture.json, official captures, and eight archived browser batches. final-corrected-dataset.json contains values, field statuses, specific unresolved reasons, evidence IDs, URLs/excerpts and source/checkpoint hashes. final-citations.json is the citation index. Browser excerpts are explicitly labeled selected rendered lines rather than complete source-page captures.

## Final field counts

| Field | Backed | Caveated | Unresolved |
|---|---:|---:|---:|
| purpose | 45 | 2 | 53 |
| auth_methods | 0 | 83 | 17 |
| api_types | 0 | 51 | 49 |
| api_available | 0 | 92 | 8 |
| api_breadth | 0 | 90 | 10 |
| access_model | 0 | 76 | 24 |
| mcp_available | 0 | 42 | 58 |
| mcp_provider | 0 | 45 | 55 |
| mcp_ownership | 0 | 37 | 63 |
| mcp_notes | 0 | 45 | 55 |
| buildability | 0 | 81 | 19 |
| buildability_rationale | 0 | 89 | 11 |
| primary_blocker | 0 | 48 | 52 |

Total: {'source_backed': 45, 'unresolved': 474, 'source_backed_with_caveat': 781}. Backed or caveated: 826/1,300; unresolved: 474/1,300.

## Remaining gaps

All critical fields unresolved: **4 apps** — Gumroad (48), fanbasis (50), Paygent Connect (84), iPayX (85). Critical fields are auth_methods, access_model, api_available, api_types, api_breadth, mcp_available and buildability.
- Gumroad: Official Gumroad API and help URLs returned no selectable body; indexed snippets cannot establish current authentication, access or full resource capabilities.
- fanbasis: Assigned Fanbasis domain now presents Commas. apidocs.fan requires JavaScript and returned only hidden bundled document content; rendered official API evidence and rebrand identity not established.
- Paygent Connect: Identity ambiguous/source unreadable: no deterministic readable official Paygent Connect source recovered
- iPayX: Current iPayX docs/developers URLs returned an FX-audit overview with no selectable developer body; indexed API/MCP descriptions were not corroborated by current rendered pages.

Other specific unresolved fields and reasons are retained for every app in the final dataset. MCP silence is not a negative claim. OAuth client authorization/scopes alone do not establish resource authentication. Product pricing alone does not establish API access. Datadog authentication remains unresolved because official material describes a transitioning model; Clay table entitlement differs across official pages and is caveated. Endpoint counts, exhaustive prerequisites and live payment eligibility are not inferred.

Unresolved reason distribution (grouping is diagnostic, not a factual classification):
- no_supported_field_evidence_or_specific_constraint: 144
- no_explicit_MCP_evidence: 216
- readiness_evidence_insufficient: 61
- docs_inaccessible_or_no_selectable_body: 26
- identity_ambiguous_or_rebrand_unestablished: 26
- conflicting_or_transitioning_documentation: 1

## Readiness distribution

- needs_further_investigation: 7
- buildable_with_documented_constraints: 62
- unresolved: 19
- gated_or_outreach_required: 11
- likely_buildable_from_public_docs: 1

Readiness is documentation-based inference only. No integration was executed and no exhaustive applicability/access certification is claimed.

## QA and protected state

- 136/136 existing tests pass (tests-final.log). Tests use mocked/offline fixtures; temporary test HTML output is not a final assessment HTML rebuild.
- 7280 retained field citation references: zero exact-text/source hash or fragment integrity errors.
- 870 frozen quota-stop artifact hashes rechecked: zero mismatches.
- 791 protected historical files unchanged; 229 tracked canonical files match.
- Canonical main clean; tracked correction diff empty; sealed production modules/history preserved.
- Supported fields all have references; counts sum to 100 apps per field and 1,300 dispositions. Positive readiness dependencies were checked.
- Citation integrity verifies exact saved evidence and provenance, not current remote-page equivalence or factual accuracy.

## Proposed fresh verification and user role

Proposed sample: **20 apps / 60 field records**, saved in proposed-fresh-verification-sample.json; all rows are NOT VERIFIED. Twelve targeted apps cover access/authentication, MCP ownership and readiness; four all-critical-unresolved apps test evidence/identity handling; four preserved automated apps cover readiness strata. All 826 supported/caveated claim candidates are indexed in verification-candidates.json.

Use an independent reviewer, open first-party source URLs anew, and record a judgment before comparing with the saved correction where feasible. Classify correct / caveat needed / unsupported / unverifiable; keep unresolved cases separate. This is a purposive risk sample, so report accuracy by stratum and do not claim a random whole-dataset accuracy estimate. If it fails, expand the affected stratum and correct source-backed claims before rebuilding final artifacts.

Your manual role is limited to judging the fresh verification outcomes, accepting the remaining caveats, and later performing/authorizing final submission steps. You do not need to research the 100 app details or buy API credits.

**Exact next action:** start the proposed fresh independent verification sample in a separate pass. This task stops before executing that sample. No final HTML rebuild, README/Notion update, deployment, Desktop copy, commit/merge/push or Form submission occurred.

Additional final checks: both sealed production modules match the preserved code snapshot; six browser-rendered excerpt documents are stored in browser-rendered-source-documents.json and match cited hashes; packaged output hash recheck passed.
