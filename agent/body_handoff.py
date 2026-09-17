"""Write an inspectable final handoff from sealed audit outputs."""
import json
import hashlib
import subprocess
import shutil
from collections import Counter
from agent import stage02 as s, coverage_correction as c, body_pilot as b

RUN='body-pilot-v3-20260917'

def projection(atoms,purpose):
    findings=b.derive(atoms,purpose)
    active=[a for a in atoms if a['retained'] and a.get('state')!='deprecated']
    if any(a['label'] in ('protocol:rest','protocol:graphql','protocol:soap','protocol:grpc') and a['mode'] in ('primary','personal','public_app') for a in active): findings['api_available']='yes'
    if any(a['label']=='mcp:provider' and 'official' in a['fact'].lower() for a in active) and any(a['label']=='mcp:availability' for a in active): findings['mcp_available']='official'
    mcp=[a['fact'] for a in atoms if a['retained'] and a['label'].startswith('mcp:')]
    if mcp: findings['mcp_notes']='; '.join(mcp)
    return findings

def main():
    d=s.ROOT/'data/correction'/RUN; out=d/'primary-audit'
    summary=s.read(out/'acceptance-decision.json'); final=s.read(out/'final-audited-results.json'); integrity=s.read(out/'integrity.json')
    raw=[s.read(p) for p in sorted((d/'apps').glob('*.json'))]
    decisions=s.read(d/'primary-decisions.json'); semantic_retained=sum(j['decision']=='retain' and j['atom_id']!='purpose' for j in decisions)
    displays=[]
    for v,r in zip(final,raw):
        baseline=projection(r.get('atoms',[]),r.get('findings',{}).get('description','unknown'))
        for field,value in baseline.items():
            if not c.known(value): continue
            retained=c.known(v['findings'][field])
            displays.append({'id':v['id'],'field':field,'decision':'retain' if retained else 'downgrade','reason':'Primary-reviewed retained atoms alone support the surface-bounded display; no replacement findings.' if retained else 'All necessary supporting atoms were downgraded for semantic or source-capture integrity failures.','baseline':value,'final':v['findings'][field],'reviewer':'primary_agent_projection_review','human_checked':False})
        assert all(not c.known(value) or c.known(baseline[field]) for field,value in v['findings'].items())
        assert all(not a['retained'] or any(x['atom_id']==a['atom_id'] and x['retained'] for x in r.get('atoms',[])) for a in v['atoms'])
    s.save(out/'display-decisions.json',displays,exclusive=True)
    body_report={'arbitrary_offset_properties':False,'selectable_ids':'complete deterministic body blocks only; no model ranges','navigation_ids_exposed':0,'retained_passages_classified_body':True,'counts':summary['body_classification_counts'],'selected_body_passages':summary['selected_body_passages'],'remaining_issues':['Nested block boundaries still split some sentences, e.g. verified-user requirement; heading context preserved but whole-paragraph reconstruction needs improvement.','Layout-token and script-boundary defects caused two interrupted attempts, both preserved.','Some link summaries/CTAs and endpoint indices still classify body; primary review must distinguish them from explanatory prose.'],'primary_audit':'Every promoted atom/purpose inspected against full saved selected body text and headings; deterministic body class is not semantic proof.'}
    s.save(out/'body-selection-audit.json',body_report,exclusive=True)
    previous={
      'strict':s.read(s.ROOT/'data/correction/strict-pilot-20260917/primary-audit-v2/final-audited-results.json'),
      'surface':s.read(s.ROOT/'data/correction/surface-pilot-20260917/primary-audit/final-audited-results.json'),
      'atomic':s.read(s.ROOT/'data/correction/atomic-pilot-20260917/primary-audit/final-audited-results.json')}
    rows=[]; comparisons=[]
    for v in final:
        counts={key:sum(c.known(x) for old in values if old['id']==v['id'] for x in old['findings'].values()) for key,values in previous.items()}
        resolved=[f for f,x in v['findings'].items() if c.known(x)]; atoms=sum(a['retained'] for a in v['atoms'])
        rows.append(f"| {v['id']} {v['app_name']} | {counts['strict']} | {counts['surface']} | {counts['atomic']} | {len(resolved)} | {atoms} | {', '.join(resolved) or 'None'} | {11-len(resolved)} |")
        comparisons.append({'id':v['id'],'prior_counts':counts,'new_display_count':len(resolved),'new_atom_count':atoms})
    s.save(out/'before-after.json',comparisons,exclusive=True)
    family_rows=[f"| {f} | {n} | {summary['atomic_retained'].get(f,0)} | {summary['atomic_downgraded'][f]} |" for f,n in summary['atomic_promoted'].items()]
    checkpoint_counts={}
    for run in ('body-pilot-20260917','body-pilot-v2-20260917',RUN):
        values=[s.read(p) for p in (s.ROOT/'data/correction'/run/'apps').glob('*.json')]
        checkpoint_counts[run]={'apps':len(values),'searches':sum(len(v['discovery']) for v in values),'readable_pages':sum(doc['ok'] for v in values for doc in v['retrievals']),'page_attempts':sum(len(v['retrievals']) for v in values)}
    s.save(out/'execution-attempt-counts.json',checkpoint_counts,exclusive=True)
    for name in ('body-tests-before.log','body-tests-approved.log','body-tests-final.log','body-pilot-run.log','body-pilot-v2-run.log','body-pilot-v3-run.log','body-pilot-seal.log'):
        shutil.copyfile(s.ROOT/name,d/name)
    code=('agent/body_pilot.py','agent/body_pilot_seal.py','agent/body_primary_decisions.py','agent/body_review_pack.py','agent/body_handoff.py','tests/test_body_pilot.py')
    s.save(d/'final-code-snapshot.json',{name:hashlib.sha256((s.ROOT/name).read_bytes()).hexdigest() for name in code},exclusive=True)
    status=subprocess.check_output(['git','status','--short'],cwd=s.ROOT,text=True)
    s.save(d/'final-working-tree.json',{'branch':integrity['checkout_branch'],'base':integrity['checkout_head'],'status':status,'tracked_diff':subprocess.check_output(['git','diff','--stat'],cwd=s.ROOT,text=True),'staged_diff':subprocess.check_output(['git','diff','--cached','--stat'],cwd=s.ROOT,text=True)},exclusive=True)
    report=f'''# Body-aware correction handoff — PILOT FAIL

Run `{RUN}`, 2026-09-17. **CORRECTION REQUIRED. safe_to_scale=false. Stopped after this fresh same-12 pilot.**

## Authoritative output and verdict

`data/correction/{RUN}/primary-audit/final-audited-results.json` is the authoritative downgrade-only atomic projection and its code-derived displays. It retains **{summary['retained_display_fields']}/132 legacy display fields and {sum(summary['atomic_retained'].values())} atoms**. This materially recovers beyond the atomic pilot's 5/132, but remains below strict's 44/132. Account/credential gates and alternative MCP/credential paths still mislabel; no app has a closed prerequisite inventory. Source-capture hashes failed on 17 pages. **Do not scale.** This sample is useful for partial investigation, but does not consistently support build/access decisions or reliable unattended research at 100-app scale.

`primary-decisions.json` records all **{len(decisions)}** primary atom/purpose judgments, with exact passage IDs and individual reasons. **213 automated atom promotions**, {semantic_retained} initially retained semantically, **{213-semantic_retained} semantic downgrades**, then **26 integrity downgrades**, leave **59 atoms**. Five purpose promotions were reviewed: four retained, LinkedIn downgraded. `display-decisions.json` separately reviews every candidate display after applying the same projection to pipeline atoms. No manually entered replacement findings, repaired source text, replacement quotes, or reclassified app atoms. Display values derive from retained atoms; protocol entails API existence, and explicitly audited official MCP provider plus retained availability can derive official availability without requiring all MCP atoms to pass.

## Exact checkout and protected state

Checkout `C:/Users/udays/.codex/.chatgpt-projects/g-p-6aaabda9d3ac8191ad4e4853ce3a6def/research-correction`.
Branch `{integrity['checkout_branch']}`; HEAD/base `{integrity['checkout_head']}`. Tracked/staged diffs remain empty. Correction code, tests and outputs remain local/untracked/uncommitted; no commits, merges or pushes.

Canonical `U:/composio-research-assessment` is clean on main at the same SHA. **229 tracked files compared byte-for-byte, zero differences.** Accepted HTML remains **{integrity['accepted_bytes']} bytes**, SHA-256 `{integrity['accepted_sha256']}`. All **{integrity['history_files_unchanged']} preflight historic files**, including atomic and earlier sealed pilots and the interrupted new attempts, are unchanged. No synced-source edits, all-100 run, final HTML rebuild, README/Notion update, deployment, Desktop copy, Form submission or history replacement. Final working-tree state is saved in `final-working-tree.json`; snapshot below.

## Code changes and rationale

- `agent/body_pilot.py`: separate runnable body-aware pilot; existing sealed correction paths remain untouched. HTML block parser preserves tag ancestry, heading and paragraph index; deterministic classes exclude hidden/title, navigation/menu/header/footer/sidebar, contact/support and short fragments. Plain text/Markdown uses whole paragraph boundaries and headings. Oversize response/block is withheld, never silently truncated into semantic evidence. Only deterministic body IDs are selectable; model schema has **no offsets or quotes**. A fair per-source character budget ranks whole paragraphs, rather than taking arbitrary windows. Source metadata includes requested/final URL, time, kind and normalized-content hash.
- Structured schema uses canonical `family:value` enums, separate personal/public_app/primary/token_exchange/enterprise/adjacent/MCP/product modes and available/required/optional/deprecated/not_required states. Atom review decisions are independent IDs; invalid or failed neighbors do not erase good atoms. Free-text fact descriptions remain, and can still become compound unsupported atoms: a remaining contract weakness.
- Auth, access, protocol, resource/action, MCP and prerequisite facts survive independently. `atomic_display_fields` preserves per-mode facts even when the old single-choice access field cannot express them. Alternative Enterprise atoms remain separate and cannot enter primary breadth. Native/plugin MCP sub-surfaces are still insufficiently distinct; affected WooCommerce plugin atoms were downgraded.
- `agent/body_pilot_seal.py`: applies primary downgrade decisions, then hash-integrity downgrades, then projects displays. MCP deprecation facts remain in notes even with deprecated state. Separate completeness objects are emitted for every observed mode plus primary, listing found prerequisites/evidence, categories not established, alternative paths, actual search queries and unresolved gaps. Buildability consumes retained atoms plus completeness state and fails closed; no model completeness flag or free-form verdict can establish it.
- `body_primary_decisions.py` stores judgments only. `body_review_pack.py` exposes complete unique source passages for primary review. `body_handoff.py` records displays/body audit, comparisons, execution counts, final code hashes and this handoff.

### Execution and final-code distinction

First attempt `body-pilot-20260917` was interrupted after script metadata spilled into the next paragraph. Second `body-pilot-v2-20260917` was interrupted after Microsoft page-wide has-left-sidebar layout classes hid actual body text. Both checkpoints/logs remain diagnostic history; neither is used as replacement evidence. Script flush boundaries and exact navigation class-token checks were fixed before v3. Final v3 retrieved all 12 apps fresh, sequentially; no cached results inflated coverage.

After v3 retrieval, integrity checks found hashes were computed before `stage02.save` scrubbed documentation credential examples. **17 saved page hashes mismatch**, including Zendesk and Stripe documents. All 26 semantically accepted dependent atoms were downgraded; no source hash was repaired and raw checkpoints were left unchanged. Final retained citations pass original saved hashes. Production capture now scrubs fragments before hashing; a real retrieval-path mock regression proves save/hash consistency. **This post-run fix was not exercised by another live pilot.** Final-code hashes describe final code, not a claim that v3 retrieval used that sanitizer fix. No fourth run was started.

## Tests and sealed-failure coverage

**106/106 full tests pass**, preserving the previous 92. Fourteen new tests in `tests/test_body_pilot.py`:

| Failure | Regression |
|---|---|
| Arbitrary/truncated fragments | Schema forbids offsets; complete deterministic blocks copied; oversize blocks excluded rather than truncated |
| Body versus nav/title | Structural navigation excluded; heading/paragraph provenance preserved |
| Bad atom erases valid atom | Independent review retains valid protocol/auth atom alongside invalid adjacent atom |
| Enum mismatch/duplication | Canonical enum schema; failed same-label atom cannot erase a good same-label atom |
| Alternative-surface poisoning | Invalid adjacent reference does not affect primary; MCP source cannot establish primary resource breadth |
| Generic HTTP inferred REST | Explicit protocol marker required |
| Incomplete prerequisite inventory | Missing categories remain explicit; model coverage_complete cannot derive buildability |
| Valid purpose discarded | Whole true product-body prose remains selectable |
| Script metadata spill (new attempt) | Script data remains hidden and cannot join following paragraph |
| Page-wide sidebar layout (new attempt) | Layout class does not hide main developer body |
| MCP breadth/deprecation projection | MCP action facts cannot enter primary breadth; seal preserves retained deprecation notes |
| Hash before serialization redaction (v3) | Production mocked retrieval, credential scrub, serialization and saved-source hash match |

Initial restricted full-suite attempts hit five known Windows temporary-directory errors; approved execution passed all tests. No tests skipped or removed. Logs are saved. The post-run capture fix has unit coverage but needs a new HQ-authorized live pilot to validate retrieval integrity end to end.

## Run IDs and commands

Existing `U:/composio-research-assessment/.venv/Scripts/python.exe` runtime and credentials; no installations or exposed/copied secrets. Run commands from the correction checkout:

```powershell
python -m unittest discover -s tests -v
python -m agent.body_pilot --run-id body-pilot-20260917       # interrupted, diagnostic only
python -m agent.body_pilot --run-id body-pilot-v2-20260917    # interrupted, diagnostic only
python -m agent.body_pilot --run-id {RUN}                    # fresh final same-12 pilot
python -m agent.body_review_pack 3 11 26 33 35 42 55 61 72 81 93
python -m agent.body_primary_decisions
python -m unittest discover -s tests -v                     # 106/106 final
python -m agent.body_pilot_seal --run-id {RUN}
python -m agent.body_handoff
```

No `--all`/cached path exists in the new runner. Same IDs **3,11,26,33,35,42,55,61,72,81,84,93**. Logs record the failed first seal assertion, followed by fail-closed integrity projection. Saved source checkpoints and previous runs are not overwritten.

## Retrieval and retention

Final v3: **60/60 successful searches; 85/90 readable page attempts; 2760 selected body passages**. These are page attempts, not unique global URLs. Parser classification counts: `{json.dumps(summary['body_classification_counts'])}`.

| Atom family | Promoted | Final retained | Downgraded (semantic + integrity) |
|---|---:|---:|---:|
{chr(10).join(family_rows)}

Derived legacy counts: `{json.dumps(summary['derived_display_counts'])}`. Access_model, buildability, buildability_rationale and primary_blocker remain **0/12 resolved**. There are **3 apps with separately retained access-gate displays** and **8 with prerequisite displays**, even though the legacy access single choice is unresolved. Atomic-family display counts: `{json.dumps(summary['atomic_family_displays'])}`. Counts of atom citations differ from previous field-citation counts and must not be compared as population accuracy.

Completed-checkpoint counts across attempts: `{json.dumps(checkpoint_counts)}`. Interrupted in-flight retrieval/model work was not checkpointed, so these are lower bounds on overall attempts/cost. Only v3 contributes to final coverage.

## Per-app resolved versus unresolved and historical pilots

| App | Strict | Surface | Atomic | New displays | New atoms | New resolved legacy fields | Unresolved /11 |
|---|---:|---:|---:|---:|---:|---|---:|
{chr(10).join(rows)}
| Total | 44 | 2 | 5 | 29 | 59 | | 103 |

Strict retrieved 48 searches/66 readable pages; surface 48/68; atomic selected attempts 60/93; v3 60/85. No monotonic-recovery guarantee: Zendesk/Stripe source-hash failures erase otherwise useful semantic findings; Apify canonical product-mode mistakes erase all its API candidates. Unknown is not validated absence and does not disprove historic findings. New atomic displays add detail absent from the old 11-field contract; compare both views, not raw atom totals against old field counts.

## Body-selection audit

No selectable model offsets, no model slices, no exposed IDs labeled navigation; every retained citation is to a deterministic body block. This materially recovers scope-correct auth/protocol/resource/MCP findings above 5/132. Primary rejection reasons now predominantly concern labels, compound claims, alternative paths and capture integrity rather than arbitrary model truncation. However, structural block splitting can still split sentences, and link summaries/CTAs/endpoint indices can still be classified body. Selection is improved, not proven universally accurate. `body-selection-audit.json` records classification and remaining defects; all retained source passages were reviewed directly.

## Auth/access/API/MCP semantic audit

Retained auth is bounded to actual resource documentation: Pipedrive token/OAuth app paths; Discord OAuth bearer resource auth; LinkedIn member OAuth consent; Mailchimp key/OAuth/Basic/Bearer with public partner-program facts separate; WooCommerce HTTPS Basic; GitHub resource Bearer; Airtable OAuth; Fathom key/SDK Bearer. Invalid PAT-as-key, OAuth1-as-OAuth2, token-exchange Basic, username-password absence-as-none, approval-as-payment, roles-as-account and Enterprise-as-primary atoms were downgraded. No identified incorrect primary surface survives this review, but the automatic reviewer endorsed many incorrect candidates; this is not measured human accuracy.

API protocol retains only Pipedrive, Mailchimp and Fathom REST; WooCommerce/Stripe REST was semantically valid but failed source-page hashes; GitHub REST atom added unsupported OpenAPI text and was downgraded. HTTP alone never establishes REST. Resource/action display is only inspected scope; it asserts no total endpoint census or population-wide API breadth.

Official MCP derives only for GitHub and Fathom from retained explicitly official provider and availability atoms. Airtable retains separate provider/availability prose; native WooCommerce retains the deprecated endpoint warning. No MCP execution or integration proof. Native/plugin WooCommerce mixing and MCP auth as resource auth were downgraded. Unknown ownership/status/limitations do not erase a valid independent atom, but do constrain aggregate conclusions.

## Purpose quality

Four concise true purposes survive: Pipedrive, Zendesk, Discord, Airtable, all <=180 characters and supported by product body prose. LinkedIn's plural-APIs capability summary bypassed the singular API text guard and was downgraded by primary review. Mailchimp/WooCommerce/Apify/GitHub/Fathom returned API/MCP purposes; Stripe selected insufficient/navigation-adjacent prose. These remain unresolved, with no manually shortened or substituted sentences. Purpose source reservation and plural API guard remain next-correction work.

## Prerequisites, completeness and buildability

13 prerequisite atoms survive in eight apps/modes. Account plan, credential eligibility, public partner review, OAuth scope/role requirements and configuration are retained separately when supported; failed neighbors do not erase them. Every surface/mode completeness object lists found prerequisites with body IDs, likely categories not established, broad queries used, alternatives and gaps. Categories are a search inventory, **not evidence of exhaustive category-specific retrieval**. All completeness states remain unestablished; buildability consumes that state and remains unknown.

WooCommerce version requirements are still omitted from prerequisites despite readable setup body. Apify optional scoped/unscoped/payment paths were mislabeled product; GitHub PAT/OAuth/local/remote paths remain incomplete. LinkedIn Development/Standard access tiers were mislabeled plan; Airtable Enterprise scopes/legacy key caveats mixed into primary modes. Stripe runtime confirmation was mislabeled app review; Zendesk valid setup/SSL prerequisites failed capture hashes. No model flag certifies completeness. No conditional/positive buildability survives; no real integration was executed.

## Citation/hash and protected-file integrity

**125/125 final retained atom/purpose citations** match saved full body text, original saved content hash, requested/final URL, retrieval time and kind. These are 125 references, with duplication across atoms/pages, not 125 independent claims. **17 source-page pre-save hash failures and 26 integrity atom downgrades** are explicit diagnostics. Raw failing hashes are unchanged; no repaired hash was represented as original. Capture-integrity pass is limited to retained citations; **overall v3 source capture failed**. Final redaction-before-hash code fix was only regression-tested and still needs fresh live validation.

Protected main/accepted artifact and all 216 preflight history files verify unchanged. Historic human overlap remains only two Paygent API-type/MCP unknown judgments, both consistent abstentions; zero fresh human checks, zero scoreable accuracy comparisons. Full historical comparison is in `historical-regression.json`.

## Remaining blockers and exact next action

**PILOT FAIL; do not scale to all 100.** Recovery to 29/132 and 59 atoms is practically useful partial research, but has no reliable primary access/completeness/buildability resolution, no findings for three apps, and a failed capture layer. Automatic support is still too permissive for wrong labels/surfaces. None of these justify authorizing 100-app unattended generation.

Next HQ-authorized correction: validate redaction-before-hash capture live; make mode meanings explicit (product only purpose, assigned resource API primary, token administration separate); split native MCP versus plugin and scoped/unscoped/local/remote/payment alternatives into distinct stable surface/path identities; reduce auth/protocol free-text compound assertions so enum-backed facts do not depend on gratuitous prose; reconstruct nested paragraph context; reserve genuine product/about evidence; reject plural API-purpose summaries; perform category-specific setup/auth/access discovery with documented coverage and an independent completeness review. Then rerun the **same 12 fresh** under a new ID, primary-audit every atom/display and rerun integrity/tests. No more live runs were performed after v3. This handoff is a recommendation, not authorization for another run.

## Final working-tree snapshot

```text
{status.rstrip()}
```
'''
    path=s.ROOT/'BODY-PILOT-HANDOFF.md'; path.write_text(report,encoding='utf-8')
    shutil.copyfile(path,d/'BODY-PILOT-HANDOFF.md')
    print('Wrote BODY-PILOT-HANDOFF.md')

if __name__=='__main__': main()
