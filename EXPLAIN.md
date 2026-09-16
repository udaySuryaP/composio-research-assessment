# Explain this project in your own words

## The 30-second explanation

“Composio needs to know whether an app is practical to integrate before building tools for it. I built a small research pipeline for the 100 supplied apps. It collects official documentation, records evidence and produces structured findings. A simple initial extractor made predictable mistakes, so I used AI assistance to inspect those mistakes and refine the rules. The case study shows the findings, unknowns, changes and verification separately. The human sample is only scored once someone actually checks the sources.”

Do not say you personally completed the human checks until you do them. Do not say the checked-in research ran through an LLM API or Composio: these optional modes were not used without credentials.

## Five things to understand

1. **An API is a way for software to interact with an app.** An agent toolkit wraps selected API actions, such as “list tickets”, with clear inputs and outputs. We did not build 100 integrations.
2. **Authentication and access are different.** OAuth explains how a user authorizes an app. It does not prove API access is free. A developer may create a test account but need review, a paid plan or an admin for production.
3. **MCP is a tool interface.** An official MCP server may provide a ready-made agent path. A local CLI can also be wrapped. An SDK is a library for writing code; Composio helps discover and execute tools, but is not mandatory for public documentation research.
4. **Unknown is useful.** A failed page fetch does not prove an app has no API. It identifies the next browser check or outreach question. “Conditional” means a documented surface exists but onboarding/production proof is still needed.
5. **Matching evidence is not accuracy.** The program can prove a quote appears on a page, yet still misunderstand it. The human sample tests that interpretation. The AI challenge set is deliberately selected and does not estimate accuracy across all 100.

## Walk through one real error

Clay’s page shows how a user calls external APIs from Clay. It includes API keys and bearer tokens for services like Stripe. The keyword first pass labelled these as Clay’s own auth. The corrected result abstains because that page does not prove Clay’s inbound API or credential path. The same principle applies to external provider credentials in BigCommerce docs.

Other examples: Harvest’s old Basic auth was mistaken for current API v2 auth; MongoDB legacy API keys use Digest while service accounts use OAuth; Otter mentions that public API keys are unavailable, so the correct official MCP path is OAuth.

## Why this architecture?

- Python with the standard library keeps setup small and easy to reproduce.
- Concurrent fetching makes 100-app collection practical.
- Caching, timestamps, hashes and exact excerpts preserve evidence provenance.
- Separate snapshots and review logs show changes instead of only the final answers.
- JSON and CSV work for agents and spreadsheets.
- A static single-page report is cheap to host and has no secrets or server to maintain.
- Optional model extraction enables unattended research later. It performs a second critique and deterministic grounding checks, but still needs human validation.

## What remains weak?

Many plan/access decisions are unresolved, and API breadth was not comprehensively inventoried. Some pages require JavaScript or return stale links. Descriptions and feasibility verdicts are labelled AI summaries/inferences. No customer API calls or credential onboarding were tested. The human sample remains pending until Uday checks it. These limits should be explained openly.

## How to complete your source check

Open the five official pages requested in the task. Write the auth methods you actually see for HubSpot, Front, Twilio and Consensus. For Clay, say whether the page describes Clay’s own inbound API or calls to other services. If a page is unavailable or ambiguous, say so; it remains unscored. Send those observations back to this task so they can be attributed to Uday and compared with the saved first and final datasets.

The broader worksheet also selects two apps per category using seed 42. More completed checks improve the submission, but they must be real checks, not copied AI conclusions.
