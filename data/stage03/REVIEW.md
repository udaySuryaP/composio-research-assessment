# Uday review — pending

Inspect the official page yourself. Confirm product identity and source ownership. Answer observed value, yes/no/unclear for first pass, proposed final value, yes/no/unclear for final, source URL and notes. Use unclear/unscored for inaccessible, ambiguous or outdated pages. Reviewer and timestamp remain blank until your review.

## Item 1: 002:auth_methods
App: HubSpot (1. CRM and Sales)
Field: auth_methods
First-pass finding: ["oauth2"]
First-pass evidence: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/oauth/working-with-oauth
Official source candidates: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/oauth/working-with-oauth
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 2: 002:access_model
App: HubSpot (1. CRM and Sales)
Field: access_model
First-pass finding: "self_serve_paid"
First-pass evidence: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/oauth/working-with-oauth
Official source candidates: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/oauth/working-with-oauth
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 3: 001:api_available
App: Salesforce (1. CRM and Sales)
Field: api_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm, https://developer.salesforce.com/docs/platform/api-rest/guide/quickstart.html, https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 4: 001:api_types
App: Salesforce (1. CRM and Sales)
Field: api_types
First-pass finding: ["unknown"]
First-pass evidence: None
Official source candidates: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm, https://developer.salesforce.com/docs/platform/api-rest/guide/quickstart.html, https://developer.salesforce.com/docs/platform/api-rest/guide/intro-oauth-and-connected-apps.html
What to verify: Which API protocols are explicitly documented for this product?

## Item 5: 095:mcp_available
App: Reducto (10. AI, Research and Media-native)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.reducto.ai/, https://docs.reducto.ai/api-reference/authentication
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.

## Item 6: 095:buildability
App: Reducto (10. AI, Research and Media-native)
Field: buildability
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.reducto.ai/, https://docs.reducto.ai/api-reference/authentication
What to verify: Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?

## Item 7: 094:primary_blocker
App: Consensus (10. AI, Research and Media-native)
Field: primary_blocker
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://consensus.app/, https://docs.consensus.app/docs/mcp
What to verify: What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.

## Item 8: 094:auth_methods
App: Consensus (10. AI, Research and Media-native)
Field: auth_methods
First-pass finding: ["unknown"]
First-pass evidence: None
Official source candidates: https://consensus.app/, https://docs.consensus.app/docs/mcp
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 9: 014:access_model
App: Front (2. Support and Helpdesk)
Field: access_model
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://dev.frontapp.com/docs/authentication.md
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 10: 014:api_available
App: Front (2. Support and Helpdesk)
Field: api_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://dev.frontapp.com/docs/authentication.md
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 11: 013:api_types
App: Freshdesk (2. Support and Helpdesk)
Field: api_types
First-pass finding: ["rest"]
First-pass evidence: https://developers.freshdesk.com/api/
Official source candidates: https://developers.freshdesk.com/api/
What to verify: Which API protocols are explicitly documented for this product?

## Item 12: 013:mcp_available
App: Freshdesk (2. Support and Helpdesk)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developers.freshdesk.com/api/
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.

## Item 13: 022:buildability
App: Twilio (3. Communications and Messaging)
Field: buildability
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://www.twilio.com/docs/usage/requests-to-twilio
What to verify: Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?

## Item 14: 022:primary_blocker
App: Twilio (3. Communications and Messaging)
Field: primary_blocker
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://www.twilio.com/docs/usage/requests-to-twilio
What to verify: What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.

## Item 15: 029:auth_methods
App: Aircall (3. Communications and Messaging)
Field: auth_methods
First-pass finding: ["oauth2", "basic"]
First-pass evidence: https://developers.aircall.io/api-references
Official source candidates: https://developers.aircall.io/api-references, https://developer.aircall.io/api-references/
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 16: 029:access_model
App: Aircall (3. Communications and Messaging)
Field: access_model
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developer.aircall.io/api-references/
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 17: 032:api_available
App: Meta Ads (4. Marketing, Ads, Email and Social)
Field: api_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developers.facebook.com/docs/marketing-apis/
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 18: 032:api_types
App: Meta Ads (4. Marketing, Ads, Email and Social)
Field: api_types
First-pass finding: ["unknown"]
First-pass evidence: None
Official source candidates: https://developers.facebook.com/docs/marketing-apis/
What to verify: Which API protocols are explicitly documented for this product?

## Item 19: 037:mcp_available
App: systeme.io (4. Marketing, Ads, Email and Social)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developer.systeme.io/docs/
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.

## Item 20: 037:buildability
App: systeme.io (4. Marketing, Ads, Email and Social)
Field: buildability
First-pass finding: "buildable"
First-pass evidence: https://developer.systeme.io/docs/api-recipes-and-how-to-use-them
Official source candidates: https://developer.systeme.io/docs/api-recipes-and-how-to-use-them, https://developer.systeme.io/docs/
What to verify: Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?

## Item 21: 041:primary_blocker
App: Shopify (5. Ecommerce)
Field: primary_blocker
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://shopify.dev/docs/api/admin-graphql, https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens
What to verify: What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.

## Item 22: 041:auth_methods
App: Shopify (5. Ecommerce)
Field: auth_methods
First-pass finding: ["bearer_token"]
First-pass evidence: https://shopify.dev/docs/api/admin-graphql/latest
Official source candidates: https://shopify.dev/docs/api/admin-graphql/latest, https://shopify.dev/docs/api/admin-graphql, https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 23: 050:access_model
App: fanbasis (5. Ecommerce)
Field: access_model
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://fanbasis.com/
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 24: 050:api_available
App: fanbasis (5. Ecommerce)
Field: api_available
First-pass finding: "yes"
First-pass evidence: https://commas.com/
Official source candidates: https://fanbasis.com/
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 25: 052:api_types
App: SE Ranking (6. Data, SEO and Scraping)
Field: api_types
First-pass finding: ["rest"]
First-pass evidence: https://seranking.com/api.html
Official source candidates: https://seranking.com/api.html
What to verify: Which API protocols are explicitly documented for this product?

## Item 26: 052:mcp_available
App: SE Ranking (6. Data, SEO and Scraping)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://seranking.com/api.html
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.

## Item 27: 054:buildability
App: MrScraper (6. Data, SEO and Scraping)
Field: buildability
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.mrscraper.com/
What to verify: Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?

## Item 28: 054:primary_blocker
App: MrScraper (6. Data, SEO and Scraping)
Field: primary_blocker
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.mrscraper.com/
What to verify: What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.

## Item 29: 064:auth_methods
App: Cloudflare (7. Developer, Infra and Data platforms)
Field: auth_methods
First-pass finding: ["bearer_token"]
First-pass evidence: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
Official source candidates: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 30: 064:access_model
App: Cloudflare (7. Developer, Infra and Data platforms)
Field: access_model
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 31: 069:api_available
App: Datadog (7. Developer, Infra and Data platforms)
Field: api_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.datadoghq.com/api/latest/authentication/
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 32: 069:api_types
App: Datadog (7. Developer, Infra and Data platforms)
Field: api_types
First-pass finding: ["unknown"]
First-pass evidence: None
Official source candidates: https://docs.datadoghq.com/api/latest/authentication/
What to verify: Which API protocols are explicitly documented for this product?

## Item 33: 080:mcp_available
App: Harvest (8. Productivity and Project Management)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.

## Item 34: 080:buildability
App: Harvest (8. Productivity and Project Management)
Field: buildability
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/
What to verify: Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?

## Item 35: 071:primary_blocker
App: Notion (8. Productivity and Project Management)
Field: primary_blocker
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://developers.notion.com/docs/authorization, https://developers.notion.com/docs/mcp
What to verify: What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.

## Item 36: 071:auth_methods
App: Notion (8. Productivity and Project Management)
Field: auth_methods
First-pass finding: ["oauth2", "bearer_token"]
First-pass evidence: https://developers.notion.com/guides/get-started/authorization
Official source candidates: https://developers.notion.com/guides/get-started/authorization, https://developers.notion.com/docs/authorization, https://developers.notion.com/docs/mcp
What to verify: Which methods authenticate the developer API? Distinguish end-user login and third-party examples.

## Item 37: 089:access_model
App: Ramp (9. Finance and Fintech)
Field: access_model
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://docs.ramp.com/developer-api/v1/overview, https://docs.ramp.com/developer-api/v1/authorization, https://docs.ramp.com/llms-full.txt
What to verify: Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?

## Item 38: 089:api_available
App: Ramp (9. Finance and Fintech)
Field: api_available
First-pass finding: "unknown"
First-pass evidence: https://docs.ramp.com/developer-api/v1/overview
Official source candidates: https://docs.ramp.com/developer-api/v1/overview, https://docs.ramp.com/developer-api/v1/authorization, https://docs.ramp.com/llms-full.txt
What to verify: Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.

## Item 39: 084:api_types
App: Paygent Connect (9. Finance and Fintech)
Field: api_types
First-pass finding: ["unknown"]
First-pass evidence: None
Official source candidates: https://paygent.io/
What to verify: Which API protocols are explicitly documented for this product?

## Item 40: 084:mcp_available
App: Paygent Connect (9. Finance and Fintech)
Field: mcp_available
First-pass finding: "unknown"
First-pass evidence: None
Official source candidates: https://paygent.io/
What to verify: Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.
