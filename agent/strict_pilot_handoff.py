"""Build a source-linked diagnostic handoff and seal the pilot, no presentation rebuild."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from agent import stage02 as s, coverage_correction as c

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    d=s.ROOT/'data/correction/strict-pilot-20260917';p=d/'primary-audit-v2'
    values=s.read(p/'final-audited-results.json');decision=s.read(p/'acceptance-decision.json')
    for v in values:
        for f,x in v['findings'].items():
            assert not c.known(x) or any(e['field']==f for e in v['evidence'])
            assert c.known(x) or v['field_status'][f]['reason'].strip()
        if v['failure']:assert all(not c.known(x) for x in v['findings'].values())
    old=s.ROOT/'data/correction/correction-pilot-cached-20260917'
    seal=s.read(old/'freeze.json')
    assert all(sha(old/name)==expected for name,expected in seal.items())
    for name in ('strict-pilot-run.log','strict-pilot-tests-before.log','strict-pilot-tests.log',
                 'strict-pilot-tests-final.log','strict-pilot-context-audit.log','strict-pilot-context-audit-retry.log'):
        shutil.copyfile(s.ROOT.parent/name,d/name)
    code=['agent/coverage_correction.py','agent/strict_pilot_audit.py','agent/strict_pilot_finalize.py',
          'agent/strict_pilot_handoff.py','tests/test_coverage_correction.py']
    s.save(d/'code-snapshot.json',{name:sha(s.ROOT/name) for name in code},exclusive=True)
    state=subprocess.check_output(['git','status','--short'],cwd=s.ROOT,text=True)
    summary=s.read(d/'summary.json')
    lines=['# Strict pilot handoff — PILOT FAIL','',
      'Recorded 2026-09-17, Asia/Calcutta. Stop point: pilot audit. **Not safe to scale to all 100.**',
      '', '## Authoritative output', '',
      '`data/correction/strict-pilot-20260917/primary-audit-v2/final-audited-results.json` is the conservative pilot projection. '
      'Raw app checkpoints, initial results, context audits and the earlier primary projection are retained as diagnostic history, not submission data. '
      'The first primary projection accidentally counted the failure-template text “Insufficient evidence.” as a populated rationale. '
      'V2 sets every failed-record finding to unknown and checks that every retained field has evidence. Earlier output is superseded, preserved and excluded.',
      '', '## Checkout and protected state', '',
      'Correction checkout: `'+str(s.ROOT)+'`. Branch: `correction/research-coverage`. HEAD: '
      '`83bd643b087da28d2e1ed1439e381b3a8a9bca7f`. All correction work is uncommitted; no tracked-file diff.',
      '', '```text',state.rstrip(),'```','',
      'Canonical `U:\\composio-research-assessment` remains clean on `main` at the same SHA. '
      '229 tracked files compared byte-for-byte with canonical: zero differences. Accepted artifact remains 81,369 bytes; SHA-256 '
      '`ea6c6914eb61e597ab8f428bd50abd7e1d5b5ca649bdeaef859bc6bd2dfab9c6`. '
      'The rejected cached pilot seal verifies all '+str(len(seal))+' listed files. Historical frozen runs/reviews/metrics/evidence were not changed. '
      'No commits, merges, pushes, Notion writes, final HTML changes, deployment, Desktop copy or Form submission.',
      '', '## Assignment alignment', '',
      'Reread `STAGE01.md` and `CORRECTION-AUDIT-HANDOFF.md`; opened the original public Notion brief in the in-app browser. '
      'The web-fetch tool failed; browser reading succeeded. Required fields are product purpose, auth, credential eligibility, API types/approximate breadth, '
      'MCP, buildability/blocker, evidence, workflow and verification. The brief explicitly accepts evidenced gates and apps that defeat research. '
      'Patterns and HTML are later phases; none were rebuilt here. `description` maps to purpose. Provider/ownership are derived from retained vendor-owned '
      'MCP claims and retain their evidence. No app findings were manually entered; primary-agent work consists of audit judgments and downgrades.',
      '', '## Selection and per-app result', '',
      'The diagnostic sample is intentionally selected, not an unbiased accuracy sample. Counts include all 11 research fields; provider/ownership are additional derived metadata.',
      '', '| App | Why selected | Resolved fields | Unresolved fields |','|---|---|---|---|']
    for v in values:
        known=[f for f,x in v['findings'].items() if c.known(x)]
        unknown=[f for f,x in v['findings'].items() if not c.known(x)]
        lines.append('| '+v['app_name']+' | '+c.SELECTION[v['id']]+' | '+str(len(known))+'/11: '+', '.join(known)+' | '+', '.join(unknown)+' |')
    lines.extend(['','## Runs, commands and tests','',
      'Runtime: existing `U:/composio-research-assessment/.venv/Scripts/python.exe`; pinned dependencies reused, no installs. '
      'Existing credentials were read locally without copying or printing them. Read-only Composio catalog inspection selected '
      '`COMPOSIO_SEARCH_TAVILY`, toolkit version `20260903_00`, using its live input schema.', '',
      '```text',
      'python -m agent.coverage_correction --run-id strict-pilot-20260917',
      'python -m agent.strict_pilot_audit --run-id strict-pilot-20260917',
      'python -m agent.strict_pilot_finalize',
      'python -m unittest discover -s tests -v',
      'python -m agent.strict_pilot_handoff','```','',
      'All commands ran in the correction checkout with the runtime above. Network-restricted catalog attempt failed with a connection error; '
      'approved network execution succeeded. Pilot: **48 successful targeted searches, 70 attempted pages, 66 readable, 4 failed; '
      '11 extraction/support-check successes and one no-readable-evidence failure**. Initial pipeline model usage: '+str(summary['model_usage'])+'. '
      'Context audit usage is separately retained per response/checkpoint; the first discarded audit-response attempt has no durable usage totals, so no complete cost/token total is claimed.',
      '', 'Tests: initial sandbox run executed 64 tests with 5 temporary-directory permission errors. Approved rerun: 64/64 pass. '
      'After three new regressions: **67/67 pass**. Stage 04 integrity checks confirm the isolated accepted HTML has equal bytes and all original 100 rows. '
      'Test success verifies code behavior, not research accuracy.',
      '', 'The first context-audit attempt rejected response cardinality and stopped without an aggregate; its failure log is retained, but raw responses from that attempt were not persisted. '
      'The resumed attempt retains raw responses, ignores unrelated decisions, and fails closed for omitted/duplicate promoted fields. '
      'It nevertheless supported every one of the 79 proposed fields, including demonstrable violations. It is a failed semantic validator, not independent verification.',
      '', '## Code changes', '',
      '- `coverage_correction.py`: 12-app selection/rationales; four targeted discovery queries; official-source selection diversified across queries (maximum 11 pages). '
      'Added guards for mixed unknown labels, overlong purposes and no-blocker conclusions with unresolved buildability.',
      '- `strict_pilot_audit.py`: separate full-retained-context adversarial audit, checkpointed raw responses/projections, strict omission/duplicate handling and all-unknown failure normalization.',
      '- `strict_pilot_finalize.py`: primary-agent downgrade-only judgments, versioned audited projection, exact quote/hash checks, historical regression and protected-file comparison.',
      '- `strict_pilot_handoff.py`: evidence-presence/unresolved-reason invariants, old rejected seal check, code hashes, retained execution logs and new pilot freeze.',
      '- Three new regression tests cover mixed unknown auth, the one-line purpose limit, and no-blocker versus unresolved prerequisites.',
      '', '## Claim and citation audit', '',
      '**79 promoted fields audited; 35 conservatively downgraded; 44 retained source-supported fields.** '
      'These are audit dispositions, not 35 proven factual errors or a measured correctness percentage. Some downgrades reflect incomplete scope/citations rather than false facts. '
      '**122/122 retained evidence entries match exact retained text, URLs, retrieval times and content hashes.** '
      'Mechanical citation success did not ensure semantic support. Numbered overlapping passages can include navigation, truncated clauses and unrelated surfaces. '
      'Raw invalid/missing references remain visible; initial deterministic guards withheld unsupported REST/access/buildability claims. '
      'Every final populated field has retained evidence and every unknown has a field-specific reason. No failed retrieval was treated as API/MCP absence.',
      '', '## MCP, access and buildability', '',
      'Retained vendor-owned MCP availability for seven apps rests on explicit product/vendor MCP evidence, not generic API pages. '
      'WooCommerce native MCP is a developer preview built on WordPress Abilities/MCP Adapter; its w7s plugin is a separate publisher and notes were withheld. '
      'Stripe is public preview; incomplete notes were withheld. Pipedrive now has explicit vendor news describing a real connector; '
      'the earlier auth-page-only MCP finding remains rejected. GitHub ownership is established by the `github/github-mcp-server` repository and GitHub-hosted remote-server text. '
      'Apify, Airtable and Fathom have explicit vendor source passages. These establish documented availability, not tested transport/client functionality.',
      '', 'Retained basic self-serve free eligibility for Apify and Airtable is bounded to documented basic/account surfaces. '
      'It does not imply free unlimited API use, all Actors, Enterprise APIs or all admin operations. GitHub paid credential eligibility was withheld. '
      'LinkedIn sources document approval applications, but the pipeline failed to express the right access classification and cited the wrong markers; '
      'access stays unresolved rather than converting advertiser/admin permissions into partnership gates.',
      '', '**All 12 buildability verdicts remain unresolved after audit.** This is the main toolkit-planning limitation: '
      'resource-auth scope, account eligibility and production/public-app prerequisites are not reliably represented. '
      'No integration or MCP client was executed, and no build-now/outreach decision is asserted from this diagnostic pilot.',
      '', '## Historical regression', '',
      'Only Paygent Connect overlaps the historical human worksheet: `api_types` and `mcp_available`. Both remain unknown, consistent with '
      'the prior identity-ambiguity finding; both historical judgments were unclear. **Two consistent abstentions, zero scoreable human comparisons, zero fresh human checks.** '
      'Browser inspection of `https://paygent.io/` redirects to `https://paygent.io/lander` and exposes no usable product text. '
      'NMI-related search results were preserved but not promoted because the assigned Paygent identity/relationship was not established.',
      '', '## Scale gate and exact next action', '',
      '**PILOT FAIL — do not scale.** The pipeline repairs mechanical evidence construction and now attempts targeted discovery, '
      'but its semantic checks repeatedly accept scope/auth/access errors. Post-audit useful facts do not prove autonomous reliability. '
      'Paygent identity and source recovery also remain incomplete.',
      '', 'Next action: within this correction checkout, add a per-surface research contract separating REST resource auth, OAuth token exchange, MCP auth, '
      'basic credential eligibility, premium/Enterprise features, permissions and production/public-app approval. '
      'Require atomic claims with body-text citations, explicit inspected breadth scope and MCP publisher/preview details. '
      'Add candidate-domain discovery with an explicit identity/ownership validation step instead of dropping every unseeded official domain. '
      'Collect targeted follow-up body passages for the currently unresolved auth/access/breadth fields; regenerate purposes rather than keeping API-centric/overlong text. '
      'Exercise the actual Zendesk/Discord/GitHub/Airtable/Apify/WooCommerce failures as regression fixtures, then rerun this same 12-app pilot under a NEW run ID and audit every claim. '
      'Keep this failed run sealed. Do not authorize a full run until that new pilot demonstrates semantic reliability.',
      '', '## Field-specific unresolved reasons', ''])
    for v in values:
        lines.extend(['### '+v['app_name'],''])
        for f,x in v['findings'].items():
            if not c.known(x):lines.append('- `'+f+'`: '+v['field_status'][f]['reason'])
        lines.append('')
    text='\n'.join(lines)+'\n'
    (d/'STRICT-PILOT-HANDOFF.md').write_text(text,encoding='utf-8')
    (s.ROOT/'STRICT-PILOT-HANDOFF.md').write_text(text,encoding='utf-8')
    seal={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='freeze.json'}
    s.save(d/'freeze.json',seal,exclusive=True)
    assert all(sha(d/name)==expected for name,expected in seal.items())
    print(json.dumps({'status':decision['status'],'sealed_files':len(seal),'rejected_prior_seal_files_valid':14,
        'handoff':str(s.ROOT/'STRICT-PILOT-HANDOFF.md')}))

if __name__=='__main__':main()
