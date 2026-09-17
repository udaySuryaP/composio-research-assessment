# Fresh independent verification handoff

**Status: VERIFICATION PARTIAL.** All identified sampled corrections are applied in a separate layer. The pre-review preserved-auth/access/breadth stratum failed materially; this is not a whole-dataset factual PASS.

Branch: `correction/research-coverage`. HEAD/base: `83bd643b087da28d2e1ed1439e381b3a8a9bca7f`. Checkout: `C:\Users\udays\.codex\.chatgpt-projects\g-p-6aaabda9d3ac8191ad4e4853ce3a6def\research-correction`. Tracked diff is empty. Work remains local, untracked and uncommitted. Exact complete working-tree listing is in `working-tree-state.json`; canonical main is clean at the same base.

## Method and sample

Fresh source observations recorded before full sample-value comparison; not fully blinded: initial handoff/sample read exposed some saved values. Reviewer is this task's agent, not a human or statistically independent second reviewer.

Current first-party pages were reopened using the web tool and browser where rendering was required. Source observations preceded full comparison where feasible; initial sample/handoff exposure prevents a fully blinded claim. No user app-detail research was required. No paid API calls, full-run restart, model/provider/key changes occurred.

Original purposive sample: **20 apps / 60 records**, three records per app. Non-overlapping selection groups: 36 targeted-correction records (12 apps), 12 preserved-automated records (4 apps), 12 unresolved/identity records (4 apps). Cross-cutting field strata below overlap; their counts must not be summed.

Apps: Klaviyo, Shopify, BigCommerce, Amazon Selling Partner, Clay, GitHub, MongoDB Atlas, Linear, Monday.com, Stripe, Datadog, PitchBook, Gumroad, fanbasis, Paygent Connect, iPayX, Intercom, GoHighLevel, HubSpot, Salesforce.

## Original pre-review outcomes

| Judgment | Records |
|---|---:|
| correct | 47 |
| caveat_needed | 8 |
| unsupported | 5 |
| unverifiable | 0 |

**Six correct records are appropriately unresolved uncertainty handling** (Paygent Connect and iPayX, three each). They are not supported positive claims. Of the 12 originally unresolved sample records, six remain appropriately unresolved and six are recoverable completion opportunities (Gumroad/fanbasis); none is an incorrect positive factual assertion.

Among the 48 originally supported/caveated records: `{"correct": 41, "caveat_needed": 2, "unsupported": 5}`. No random-sample or whole-dataset accuracy estimate is justified.

| Stratum | Records | correct | caveat_needed | unsupported | unverifiable | Appropriately unresolved |
|---|---:|---:|---:|---:|---:|---:|
| targeted corrections | 36 | 34 | 1 | 1 | 0 | 0 |
| MCP | 4 | 4 | 0 | 0 | 0 | 0 |
| access/auth | 27 | 20 | 3 | 4 | 0 | 2 |
| readiness | 22 | 19 | 3 | 0 | 0 | 2 |
| preserved automated findings | 12 | 7 | 1 | 4 | 0 | 0 |
| unresolved/identity cases | 12 | 6 | 6 | 0 | 0 | 6 |

## Bounded expansion

15 additional field records were reviewed, separate from the original 60: four preserved auth records (Pipedrive, Attio, Twenty, Podio), plus eleven same-app Salesforce/Gumroad/fanbasis onboarding, resource and readiness dependencies. The auth expansion found the three supported lists acceptable with existing non-exhaustive caveats, and resolved Podio's unknown OAuth2 field. Same-app expansion completed recoverable evidence and scoped readiness. It did not expand MCP because all four sampled ownership records passed. Expansion outcomes are recorded independently in `expanded-verification-judgments.json`.

Failure mode: unsupported authentication taxonomy labels and imported UI permissions; a generic product blog also overstated endpoint breadth. Expansion bounds the mechanism, not the prevalence across unsampled apps. GitHub Basic is retained only for app client ID/secret on selected endpoints, not username/password. Attio also documents token Basic delivery; its existing list was non-exhaustive.

## Every correction

25 field corrections across 8 apps. Original values, statuses and references are preserved in `field-corrections.json`. All replacements are source-backed with caveats; source notes are labeled paraphrases rather than falsely exact quotes. The new dataset is `final-corrected-dataset.json` and its citation index is `final-citations.json`.

| App / field | Original value (status) | Pre-review judgment | Corrected value / status | Official source |
|---|---|---|---|---|
| GitHub / auth_methods | ["personal_access_token", "basic", "oauth2", "bearer_token", "service_account", "api_key"] (source_backed_with_caveat) | unsupported | ["personal_access_token", "basic", "oauth2", "bearer_token"]; source_backed_with_caveat | [official](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api) |
| GoHighLevel / auth_methods | ["oauth2", "api_key", "service_account"] (source_backed_with_caveat) | unsupported | ["oauth2", "bearer_token"]; source_backed_with_caveat | [official](https://marketplace.gohighlevel.com/docs/Authorization/PrivateIntegrationsToken/index.html)<br>[official](https://marketplace.gohighlevel.com/docs/Authorization/OAuth2.0/) |
| HubSpot / auth_methods | ["oauth2", "personal_access_token"] (source_backed_with_caveat) | unsupported | ["oauth2", "bearer_token"]; source_backed_with_caveat | [official](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview) |
| HubSpot / access_model | [{"gate": "credential_creation", "surface": "primary", "qualification": "Developers can create apps and obtain client ID and secret via the HubSpot developer platform.", "atom_id": "a10"}, {"gate": "admin_permission", "surface": "primary", "qualification": "Certain OAuth scopes like crm.objects.users.read require the user to have Super Admin or 'Add and edit users' permissions to authorize.", "atom_id": "a14"}, {"gate": "admin_permission", "surface": "primary", "qualification": "Super Admin permission is required to set up content approval workflows and approve content in HubSpot.", "atom_id": "a17"}, {"gate": "admin_permission", "surface": "primary", "qualification": "Super Admin permissions are required to export payment reports in HubSpot payments.", "atom_id": "a19"}] (source_backed_with_caveat) | unsupported | [{"gate": "credential_creation", "surface": "primary", "qualification": "Create app credentials; OAuth for multi-account apps or static bearer auth for a single account. Requested resource scopes and account-tier entitlement apply; UI approval/payment-export permissions are not generic API onboarding gates.", "atom_id": "verification-2-access"}]; source_backed_with_caveat | [official](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview)<br>[official](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/scopes) |
| Amazon Selling Partner / access_model | [{"gate": "registration", "surface": "primary", "qualification": "SP-API developer and application registration required; public apps must be listed in the Selling Partner Appstore.", "atom_id": "targeted-49-access"}] (source_backed_with_caveat) | caveat_needed | [{"gate": "credential_creation", "surface": "primary", "qualification": "Register developer/application and obtain relevant selling-partner authorization. Restricted data may need RDT. Public app distribution/listing policy is route-specific and inconsistent across currently indexed official guidance; verify applicable policy before distribution.", "atom_id": "verification-49-access"}]; source_backed_with_caveat | [official](https://developer-docs.amazon/sp-api/docs/connecting-to-the-selling-partner-api)<br>[official](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) |
| Salesforce / api_breadth | "Inspected documented actions: Salesforce platform allows managing business logic, workflows, and AI agents via APIs and platform tools." (source_backed_with_caveat) | unsupported | "REST resources include records, collections, query results, metadata and API information; documented resource operations access, create and manipulate data."; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm) |
| Salesforce / auth_methods | ["unknown"] (unresolved) | caveat_needed | ["oauth2"]; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html) |
| Salesforce / api_types | ["unknown"] (unresolved) | caveat_needed | ["rest"]; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm) |
| Salesforce / access_model | "unknown" (unresolved) | caveat_needed | [{"gate": "credential_creation", "surface": "primary", "qualification": "Org edition and user API Enabled permission required; Professional edition needs API add-on. Use external client app OAuth; creating connected apps is restricted from Spring 26.", "atom_id": "verification-1-access"}]; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html) |
| Salesforce / buildability | "needs_further_investigation" (source_backed_with_caveat) | caveat_needed | "buildable_with_documented_constraints"; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html) |
| Salesforce / buildability_rationale | "Core resource evidence retained, but credential onboarding or coherent auth/API support is incomplete." (source_backed_with_caveat) | caveat_needed | "REST resources, OAuth and API-enabled org/user onboarding documented. Edition/permission and Spring 26 connected-app restrictions apply; no execution certification."; source_backed_with_caveat | [official](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html)<br>[official](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html) |
| Gumroad / auth_methods | ["unknown"] (unresolved) | caveat_needed | ["oauth2"]; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / api_available | "unknown" (unresolved) | caveat_needed | "yes"; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / api_types | ["unknown"] (unresolved) | caveat_needed | ["rest"]; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / api_breadth | "unknown" (unresolved) | caveat_needed | "Inspected documented resource methods cover products, sales, subscriptions and user public information."; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / access_model | "unknown" (unresolved) | caveat_needed | [{"gate": "credential_creation", "surface": "primary", "qualification": "Register OAuth application, obtain application ID/secret and generate own access token, or authorize OAuth with scopes; license verification is a separate route.", "atom_id": "verification-48-access"}]; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / buildability | "unresolved" (unresolved) | caveat_needed | "buildable_with_documented_constraints"; source_backed_with_caveat | [official](https://gumroad.com/api) |
| Gumroad / buildability_rationale | "unknown" (unresolved) | caveat_needed | "OAuth application/token onboarding and REST resource methods documented; scopes and authorization apply. No integration executed."; source_backed_with_caveat | [official](https://gumroad.com/api) |
| fanbasis / auth_methods | ["unknown"] (unresolved) | caveat_needed | ["api_key"]; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| fanbasis / api_available | "unknown" (unresolved) | caveat_needed | "yes"; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| fanbasis / api_breadth | "unknown" (unresolved) | caveat_needed | "Inspected documented checkout-session creation and payment-link response; docs also describe subscriptions and webhooks."; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| fanbasis / access_model | "unknown" (unresolved) | caveat_needed | [{"gate": "credential_creation", "surface": "primary", "qualification": "Commas dashboard Account -> API Keys generates a scoped key; requests to www.fanbasis.com production endpoints include x-api-key. Exact brand mapping limited to documented host.", "atom_id": "verification-50-access"}]; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| fanbasis / buildability | "unresolved" (unresolved) | caveat_needed | "buildable_with_documented_constraints"; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| fanbasis / buildability_rationale | "unknown" (unresolved) | caveat_needed | "Scoped key issuance and checkout resource requests documented for explicitly identified fanbasis.com host. Rebranded Commas docs mapping caveat retained; no integration executed."; source_backed_with_caveat | [official](https://apidocs.fan/api/basics) |
| Podio / auth_methods | ["unknown"] (unresolved) | caveat_needed | ["oauth2"]; source_backed_with_caveat | [official](https://developers.podio.com/authentication) |

## Post-correction state and checks

100 apps / 1,300 field dispositions: 45 source_backed, 798 source_backed_with_caveat, 457 unresolved. These counts describe evidence disposition, not measured accuracy. Corrected-after-review values are not counted as fresh independent successes. Original 60 judgments remain unchanged.

Citation/integrity errors: **0**. Retained historical citations were matched to the protected baseline and their exact snippets/source-text hashes rechecked against checkpoint/capture sources. New source/archive hashes and references were checked; selected browser transcriptions are explicitly distinguished from full-page archives. All 37 protected previous-layer output hashes and 870 frozen checkpoint hashes match. All 791 historical files and 229 canonical tracked files remain unchanged. Canonical main and tracked checkout are clean. **136/136 existing tests pass**; tests use mocked/offline fixtures, and temporary test HTML is not a final assessment rebuild.

## Readiness, blockers and next action

The corrected layer is ready for uncertainty-aware whole-dataset pattern analysis, subject to the user reviewing/accepting these outcomes. Final HTML rebuilding should follow that acceptance in the next stage. This pass performed no final HTML rebuild, README/Notion update, deployment, Desktop copy, commit, merge, push or submission.

Paygent Connect remains identity-ambiguous despite a candidate page naming the product; iPayX docs remain unreadable. No facts were invented for either. Amazon public-listing guidance conflicts across first-party indexed pages, some blocked when reopened; the correction keeps registration and authorization established but preserves listing-policy applicability as unresolved rather than asserting a universal gate. Clay table entitlement and Datadog planned-vs-current migration caveats remain conservative. Readiness means documentation-based inference, not a working integration or exhaustive prerequisite certification.

Exact next action: the user reviews and accepts `original-sample-judgments.json`, `field-corrections.json` and this handoff. No manual app-detail research is needed. After acceptance, proceed to whole-dataset patterns and final HTML in a separately authorized stage.
