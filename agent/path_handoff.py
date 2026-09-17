"""Generate the final local handoff from sealed primary review only."""
import hashlib
import json
import subprocess
from collections import Counter
from agent import stage02 as s, coverage_correction as c

RUN='path-pilot-20260917'

def main():
 d=s.ROOT/'data/correction'/RUN; out=d/'primary-audit'
 final=s.read(out/'final-audited-results.json'); result=s.read(out/'acceptance-decision.json'); state=s.read(out/'integrity.json')
 raw=[s.read(x) for x in sorted((d/'apps').glob('*.json'))]
 capture=s.read(s.ROOT/'data/correction/capture-validation-live-20260917/capture-integrity.json')
 prior={
  'strict':s.read(s.ROOT/'data/correction/strict-pilot-20260917/primary-audit-v2/final-audited-results.json'),
  'surface':s.read(s.ROOT/'data/correction/surface-pilot-20260917/primary-audit/final-audited-results.json'),
  'atomic':s.read(s.ROOT/'data/correction/atomic-pilot-20260917/primary-audit/final-audited-results.json'),
  'body_v3':s.read(s.ROOT/'data/correction/body-pilot-v3-20260917/primary-audit/final-audited-results.json')}
 comparisons=[]; rows=[]
 for v in final:
  counts={name:sum(c.known(x) for old in values if old['id']==v['id'] for x in old['findings'].values()) for name,values in prior.items()}
  resolved=[f for f,x in v['findings'].items() if c.known(x)]
  atom_count=sum(a['retained'] for a in v['atoms'])
  comparisons.append({'id':v['id'],'historical_displays':counts,'new_displays':len(resolved),'new_atoms':atom_count,'resolved':resolved,'unresolved':11-len(resolved),'buildability_unresolved_reason':v['buildability_unresolved_reason']})
  rows.append(f"| {v['id']} {v['app_name']} | {counts['strict']} | {counts['surface']} | {counts['atomic']} | {counts['body_v3']} | {len(resolved)} | {atom_count} | {', '.join(resolved) or 'None'} | {11-len(resolved)} |")
 s.save(out/'before-after.json',comparisons,exclusive=True)
 decisions=s.read(d/'primary-decisions.json'); purpose=[j for j in decisions if j['atom_id']=='purpose']
 search_audit=[]
 for v in raw:
  for log in v['discovery']:
   urls=s.urls(log.get('response',{}))
   docs=[{'requested_url':doc['requested_url'],'final_url':doc['final_url'],'ok':doc['ok'],'source_kind':doc['source_kind']} for doc in v['retrievals'] if doc['requested_url'] in urls]
   search_audit.append({'id':v['id'],'category':log['category'],'query':log['query'],'ok':log['ok'],'returned_urls':urls,'retrieved_results':docs,'search_scope':'app-wide category search; not independent per-path discovery'})
 s.save(out/'prerequisite-search-audit.json',search_audit,exclusive=True)
 path_audit=[{'id':v['id'],'atom_id':a['atom_id'],'label':a['label'],'path_id':a['path_id'],'state':a['state'],'retained':a['retained'],'primary_reason':a.get('primary_audit',{}).get('reason',a.get('audit_reason'))} for v in final for a in v['atoms']]
 s.save(out/'path-semantic-audit.json',path_audit,exclusive=True)
 s.save(out/'purpose-audit.json',purpose,exclusive=True)
 historic=s.read(out/'historical-regression.json')
 app_notes={
  3:'No atoms/purpose survive. Unsupported commercial/dimension assertions; purpose body was security prose supported only by accumulated marketing headings.',
  11:'Product purpose survives. OAuth was mislabeled unscoped; token administration and Enterprise features entered primary setup paths. Verified-user sentence remains split.',
  26:'Scoped OAuth resource auth, read/create/update facts and required scope setup survive in path displays. Bot credentials/permissions and privileged-intent review remain distinct unresolved routes. Generated purpose exceeded 180 characters.',
  33:'No findings survive. OAuth unscoped identity, approval-as-plan/payment, adjacent Conversions/Events evidence and developer-only purpose failed.',
  35:'Authorizing-user role prerequisite survives. Marketing/Transactional and personal/public credential paths are mixed; lifetime is not scope evidence; purpose adds unsupported audience/email details.',
  42:'No atoms survive. No-payment/unscoped assertions are unsupported, permalinks are not registration, W7S plugin is mislabeled native. Version requirements were retrieved but no supported version prerequisite survived.',
  55:'No atoms survive. Scoped token setup is mislabeled unscoped; external MCP client connector auth is assigned Apify native MCP; Actor user approvals become admin/partner gates; free-plan credits become trial.',
  61:'No atoms survive. No-payment assertions are unsupported; Basic/token administration enters resource auth, Docker local setup enters remote MCP, public image becomes anonymous auth, Enterprise setup enters generic native path.',
  72:'Product purpose survives. Token deletion becomes resource deletion, retired keys become auth:none, Enterprise compound claims overreach, documentation login becomes API registration, MCP no-additional-charge evidence becomes unscoped/no-payment identity.',
  81:'Product purpose survives. Generic key/REST evidence is assigned unsupported unscoped route; public-app/Connect/MCP paths remain mixed, support plans become payment eligibility, consulting becomes partner approval, publishable-key safety becomes anonymous auth.',
  84:'Official paygent.io remains unreadable/too short. Identity search retrieved third-party Spreedly/NMI documents; all 11 proposed NMI atoms were deterministically rejected. No assigned-product evidence, purpose, auth/API/MCP/prerequisites or buildability established.',
  93:'User-scoped API-key auth and meeting/transcript reads survive in path displays. Public OAuth is mislabeled primary, OAuth scope is mislabeled unscoped, rate limits become paid-plan gate, MCP scope unsupported; developer-only purpose rejected.'}
 notes='\n'.join(f"- **{v['id']} {v['app_name']}**: {app_notes[v['id']]} Buildability unresolved: {v['buildability_unresolved_reason']}" for v in final)
 code=['agent/body_pilot.py','agent/path_contracts.py','agent/path_pilot.py','agent/path_audit.py','agent/path_handoff.py','tests/test_path_pilot.py']
 s.save(d/'final-code-snapshot.json',{name:hashlib.sha256((s.ROOT/name).read_bytes()).hexdigest() for name in code},exclusive=True)
 working={'branch':state['branch'],'base':state['head'],'status':subprocess.check_output(['git','status','--short'],text=True),'tracked_diff':subprocess.check_output(['git','diff','--stat','HEAD'],text=True),'staged_diff':subprocess.check_output(['git','diff','--cached','--stat'],text=True)}
 s.save(d/'final-working-tree.json',working,exclusive=True)
 families=sorted(set(result['promoted_atoms'])|set(result['retained_atoms']))
 family_rows=[f"| {f} | {result['promoted_atoms'].get(f,0)} | {result['retained_atoms'].get(f,0)} | {result['promoted_atoms'].get(f,0)-result['retained_atoms'].get(f,0)} |" for f in families]
 total_atoms=sum(result['retained_atoms'].values())
 full_extracted=Counter(a['label'].split(':')[0] for v in raw for a in v.get('atoms',[]))
 report=f'''# Path correction handoff — PILOT FAIL

**CORRECTION REQUIRED. safe_to_scale=false. Stopped after the fresh same-12 corrected pilot `{RUN}`.**

## Authoritative results and verdict

`data/correction/{RUN}/primary-audit/final-audited-results.json` is the authoritative downgrade-only output. **{total_atoms} atoms and {result['retained_display_fields']}/132 legacy displays survive**. `{len(decisions)}` primary judgments cover every automated promoted atom and purpose; each contains a reason. No source text, selected citation, extracted path, or app finding was manually replaced. Displays are projections of retained exact-path atoms. `display-decisions.json` audits every candidate legacy display; path displays contain the individually reviewed atoms themselves.

Capture is repaired on live retrieval, but useful decision-oriented integration retention is not materially stronger or stable. Unsupported dimension assertions, coarse route identity, incomplete discovery by actual surface, body reconstruction gaps and prerequisite closure still prevent a Composio member from making reliable build/investigate/outreach decisions without manually reconstructing source requirements. No numeric pass threshold was invented. **Do not scale to 100.**

## Exact branch, base and working tree

Checkout: `{s.ROOT.as_posix()}`. Branch `{state['branch']}`, HEAD/base `{state['head']}`. Tracked and staged diffs are empty. All changes and results remain local/untracked/uncommitted. Exact full status is in `final-working-tree.json`.

Canonical `U:/composio-research-assessment` remains clean on `{state['canonical_branch']}` at `{state['canonical_head']}`. **{state['tracked_files_compared']} tracked files compared byte-for-byte; zero differences. {state['history_files']} preflight history files unchanged**, including the sealed body-v3, atomic, surface and strict artifacts and the capture-validation checkpoints. Accepted HTML: {state['accepted_bytes']} bytes; SHA-256 `{state['accepted_sha256']}`. No synced `sources/` edits, all-100 run, final HTML build, README/Notion update, deployment, Desktop copy, Form submission, commit, merge or push.

## Code changes and rationale

- `agent/path_contracts.py`: explicit mode definitions (`product` purpose only, assigned resource `primary`, `token_admin`, `personal_integration`, `public_app`, `enterprise`, `adjacent`, `mcp_native`, `mcp_plugin`). Stable IDs additionally separate scope, transport and commercial dimensions; unspecified dimensions make no universality claim. Personal access tokens and OAuth1 have their own canonical atomic labels; legacy projection can express them only as `other`.
- Auth/access/protocol/API facts use canonical enum values plus passage IDs. The optional note can be empty. These families no longer need redundant compound fact prose. Resource, MCP and prerequisite notes still need concise complete support. Canonical MCP ownership labels permit same-path ownership/availability projection.
- `agent/path_pilot.py`: separate fresh-only same-12 runner. Nested heading stacks preserve parent headings across HTML and Markdown whole body blocks; navigation remains non-selectable. Product evidence has a separately reserved 30k-character whole-passage budget. Purpose rejects singular/plural APIs and developer descriptions, remains <=180 characters. A separate identity query runs when the seeded website is malformed; Paygent results remain untrusted unless deterministic official-origin rules establish identity.
- Category-specific searches cover account eligibility, credential issuance, OAuth registration, scopes/roles, administration, review, plan/payment, partner/sales, configuration and version, plus product/protocol/MCP discovery. Search responses, returned URLs, retrieved results and failures are saved. Selection takes up to two official results per category with a 32-source cap, not cached outputs.
- Capture checks run before extraction after sanitization and again after saving. Full fragments, saved text, saved page hash and selected passage hash must agree; mismatches fail closed. The original redaction-before-hash production fix was exercised live; original v3 failing hashes were never repaired.
- `agent/path_audit.py`: primary pack and seal, expected-judgment coverage assertion, downgrade-only exact-path projection, source/citation integrity, protected history/canonical comparison, human-overlap comparison. Native ownership cannot satisfy plugin availability, and personal/public/admin/Enterprise paths cannot satisfy primary resource fields.
- Independent deterministic inventory review consumes retained prerequisite atoms and actual query records, not extraction assertions. It cannot establish exhaustive applicability/alternative-path closure from search completion; all incomplete paths stay unresolved. Buildability is derived as unknown, with precise missing primary categories and path-closure reasons outside the legacy unknown fields.
- `agent/path_handoff.py`: source-backed count/comparison/search/path/purpose artifacts and this handoff.

### Execution distinction and remaining implementation limits

Fresh capture validation used the existing body runner, before launching the corrected runner. Capture-validation extraction outputs are **unaudited diagnostics**, never merged into corrected findings. The earlier restricted-network attempt `{ 'capture-validation-20260917' }` stopped at the Composio catalog before any search/page/app checkpoint. The approved live attempt used `{capture['run_id']}`. Code snapshot at corrected-run start and final hashes distinguish retrieval code from the subsequently added reporting code.

The corrected extractor still assigns unsupported scope/transport/commercial dimensions. The automatic reviewer accepted many; primary review downgrades whole proposed atoms rather than silently repairing their path. This is a regression in useful retention, not evidence that historical facts ceased to exist. Stable mode enums do not by themselves establish semantic identity. Local/remote transport is meaningful for MCP deployment but was also over-applied to resource APIs. `unspecified` is a stable identity value but does not close known alternatives. The current identity tuple lacks a separate credential-route discriminator beyond mode/scope/transport/commercial; it cannot certify complete inventories for PAT versus OAuth or multiple native products sharing a mode.

Nested heading preservation is improved, but the parser still splits inline/block requirements and accumulates headings that can supply a broad marketing claim without matching body purpose prose. Primary purpose review rejects that case. Source blocks are whole deterministic units, not reconstructed arbitrary slices. Category searches are genuinely app-wide category-specific calls; they are **not yet separate category searches for every identified path/surface**. `prerequisite-search-audit.json` states this limit explicitly. Search completion is not prerequisite completeness.

## Tests and failures covered

**119/119 full tests pass**, preserving all 106 body-v3 tests. Thirteen new tests in `tests/test_path_pilot.py` cover:

| Regression | Failure prevented |
|---|---|
| Stable/disjoint path IDs | personal/public/admin/MCP/Enterprise identities collapse |
| Alternative-path primary projection | one route establishes a different route's resource auth |
| Token administration/resource auth | issuance credential labels establish resource access |
| Native/plugin MCP distinction | plugin evidence is assigned native identity |
| Same-path MCP ownership/availability | ownership on one surface establishes another's availability |
| Product reserved for purpose | integration atoms enter product mode |
| Enum fact normalization | gratuitous compound prose is mandatory for canonical auth facts |
| Plural API purpose guard | APIs capability summaries pass singular-only guard |
| Nested context/navigation exclusion | setup subsection loses parent heading or imports nav noise |
| Actual category query bookkeeping | generic query is represented as searched category |
| Independent completeness | extraction coverage_complete certifies buildability |
| Saved content/page/citation hash check | serialization or retained citation diverges from hash |
| Mock category-specific search calls | category inventory is claimed without actual calls |

Existing production retrieval/redaction regression and all atomic/surface protections remain passing. Restricted full-suite execution hit the five known Windows temporary-directory permission errors; approved execution passed with no test skipped. The suite was rerun after all 12 checkpoints and primary judgments: **119/119 pass**, in `path-tests-postpilot.log`. Other logs: `path-tests-before.log`, `path-tests-approved.log`, `path-tests-final.log`. Tests verify mechanics and fail-closed behavior, **not live model semantic correctness**; the live primary audit demonstrates that remaining failure.

## Run IDs and commands

Runtime: `U:/composio-research-assessment/.venv/Scripts/python.exe`; existing credentials loaded in-process, no installs or copied secrets. Commands from correction checkout:

```powershell
python -m agent.body_pilot --run-id capture-validation-20260917  # restricted network failure; no apps
python -m agent.body_pilot --run-id {capture['run_id']}  # successful fresh same-12 capture validation
python -m unittest tests.test_path_pilot -v
python -m unittest discover -s tests -v
python -m agent.path_pilot --run-id {RUN}  # fresh corrected same-12 retrieval
python -X utf8 -m agent.path_audit --run-id {RUN} --pack 3 11 26 33 35 42 55 61 72 81 84 93
python -X utf8 -m agent.path_audit --run-id {RUN}
python -m agent.path_handoff
```

The capture-integrity and per-app primary-decision records were written by local review commands. No manual replacement findings. `path-pilot-run.log` contains the corrected checkpoints. `--all` and cached-output options do not exist. Sample is exactly **3,11,26,33,35,42,55,61,72,81,84,93**.

## Retrieval and live capture integrity

First successful live validation: **{capture['search_successes']}/{capture['search_attempts']} successful searches; {capture['readable_pages']}/{capture['page_attempts']} readable page attempts; 12/12 apps checkpointed; zero capture mismatches**. Every saved retrieval, including non-readable attempts, is checked for fragments/text/hash agreement after all redaction. Diagnostic passage texts agree with saved pages; that runner did not persist a separate hash in each passage. The corrected runner additionally persists and validates every selected passage hash against its saved page, and the seal copies those matching hashes into retained citations. No semantic validation or primary promotion from the diagnostic run is claimed.

Corrected pilot: **{result['search_successes']}/{result['search_attempts']} successful searches; {result['readable_pages']}/{result['page_attempts']} readable page attempts; zero source-capture errors**. Category attempt counts: `{json.dumps(result['category_searches'])}`. Page counts are attempts, not unique global sources. Fresh retrieval only. Failures: `{json.dumps(result['failures'])}`. Hash checks are recorded per app in `capture-checks/` and repeated by the seal.

## Retained and downgraded atoms/displays

Raw extracted atoms by family: `{json.dumps(dict(full_extracted))}`. The following promotions are automated-retained candidates entering primary review; downgrade counts exclude already rejected raw extractions:

| Family | Promoted | Retained | Downgraded |
|---|---:|---:|---:|
{chr(10).join(family_rows)}

Legacy display counts: `{json.dumps(result['display_counts'])}`; **{result['retained_display_fields']}/132** retained. Buildability/access unresolved is not validated absence. Exact path displays preserve only surviving audited atoms; they are not inflated into primary legacy fields.

## Per-app resolved/unresolved and comparison

| App | Strict | Surface | Atomic | Body-v3 | New displays | New atoms | Resolved legacy fields | Unresolved /11 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
{chr(10).join(rows)}

{notes}

Historic display totals: **strict 44/132, surface 2/132, atomic 5/132, body-v3 29/132**, versus **{result['retained_display_fields']}/132** corrected. Body-v3 retained 59 atoms/125 citation references with 17 failed page hashes and 26 integrity downgrades; atomic retained 5 displays. Atom counts and legacy display/citation counts are different populations, not accuracy estimates. Strict 48 searches/66 readable pages; surface 48/68; atomic 60/93; body-v3 60/85. New counts are given above. No monotonic recovery is claimed.

## Path, purpose, auth/access/API/MCP primary audits

Every promoted atom/purpose was read against its complete selected body passages and heading context. `primary-decisions.json`, `path-semantic-audit.json`, `purpose-audit.json`, `display-decisions.json` and `citation-quality.json` are inspectable judgments/evidence. Primary review is an agent review, **not new human accuracy data**.

Unsupported path dimensions fail as unsupported facts even when a core auth/protocol label is otherwise useful. Token issuance is not resource authentication. Personal and public registration paths, Enterprise feature gates, native MCP, plugin MCP and payment/scoped/local alternatives do not satisfy each other. Enum auth facts are independent from neighbors and redundant prose, but assigning unsupported dimensions still makes the atom compound; valid core facts are lost rather than manually relabeled. REST requires explicit REST evidence; generic HTTP never suffices. MCP ownership requires explicit evidenced ownership and matching availability, not official-domain inference. Purpose retains only concise genuine product body prose; security/endpoint/developer descriptions and plural APIs summaries are rejected. Purpose promotions: {len(purpose)}; retained: {sum(x['decision']=='retain' for x in purpose)}.

## Prerequisite discovery/completeness and buildability audits

Actual category queries, URLs returned, pages attempted and independent evidence attribution are recorded in `prerequisite-search-audit.json`. Per-path reviews list individually evidenced prerequisite atoms and unresolved categories. More specific search activity does not yet yield complete, scope-correct inventories. Some extracted setup atoms still use resource modes for issuance, or mix plan features with core access. Search bookkeeping has materially improved inspectability, but not established reliable per-surface coverage or decision usefulness.

Completeness remains **unresolved for every app**. Independent review is deterministic and cannot be satisfied by extraction assertions; it explicitly cannot close applicability or alternative-path completeness from current evidence. It currently has no evidenced closure mechanism that could certify a fully enumerated path. Consequently **all 12 buildability results remain unknown**. Each final app has `buildability_unresolved_reason` listing missing primary categories and unresolved alternative-path applicability. No model-authored positive/conditional verdict, evidence from silence, or executed integration claim survives.

Paygent recovery is deterministic/search-based: malformed seeded website triggers an identity query and diagnostic candidate retrieval, without manually replacing assigned app data or trusting NMI as the assigned product. Ambiguous/unreadable identity remains unresolved. No adjacent provider data is substituted.

## Citation/hash and historical human-review regression

**{result['exact_citations']}/{result['citations']} retained citation references verify exactly** against saved whole body text and post-redaction hashes. Citation/page hash assertions are fail closed; zero corrected source-capture mismatches. The diagnostic run and corrected run each validate their own fresh saved sources. No original v3 hashes or history were altered.

Historical overlap: `{json.dumps(historic)}`. These are the existing two Paygent unknown API-type/MCP judgments where overlap exists; no fresh human checks and no scoreable new population accuracy are claimed.

## Remaining blockers and exact next action

**PILOT FAIL; safe_to_scale=false. Stop here.** Capture integrity is live-validated, tests pass and protected state is unchanged. Integration retention is not materially stronger or stable enough for Composio member decisions. More retrieval exposed unsupported path dimensions and insufficient per-surface discovery rather than closing prerequisites.

Next HQ-authorized correction: make route identity an independently evidenced contract (credential type, distribution, MCP product/adapter and deployment/payment variants), represent unknown dimensions as unasserted rather than forcing compound facts, bind each asserted dimension to its own passage IDs, and make deterministic review reject unsupported identity before promotion. Keep core enum facts independent of separately failing dimensions without silently reclassifying app evidence. Reconstruct full parent paragraphs/body context; bind product purpose to genuine product sentences. Perform category-specific searches for every actual discovered surface/route with explicit applicability evidence, and add an independent completeness closure mechanism requiring a traceable setup checklist and alternative-path disposition. Regression-test the concrete live mislabels, then run and primary-audit the same 12 fresh only under new authorization. Do not start 100-app work or publish any artifacts.

## Full final working-tree status

```text
{working['status'].rstrip()}
```
'''
 (s.ROOT/'PATH-PILOT-HANDOFF.md').write_text(report,encoding='utf-8')
 print({'status':result['status'],'safe_to_scale':False,'atoms':total_atoms,'displays':result['retained_display_fields'],'handoff':'PATH-PILOT-HANDOFF.md'})

if __name__=='__main__': main()
