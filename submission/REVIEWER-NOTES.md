# Uday reviewer notes

1. **What did you build?** A 100-app research pipeline, retained evidence, a deterministic human sample, verified-only projection and a self-contained interactive case study.
2. **Why not manually research everything?** Structured collection made identities, schema, provenance and failures consistent; human judgment remained necessary for semantic truth.
3. **Where did Composio help?** After correcting the Platform Project key, eight successful COMPOSIO_SEARCH_TAVILY searches augmented research separately at version 20260903_00. The complete baseline used seed-document fallback.
4. **Why was first pass poor?** Of 28 sample misses, 25 were unknowns later resolved; three known values were wrong or incomplete. Retrieval gaps, auth distinctions, access gates and identity ambiguity required review.
5. **What does 7/35 → 35/35 mean?** The same 35 scoreable sampled claims improved from 20% to 100%; five of 40 were unscored. Final judgments were supplied during verification. This is not dataset-wide accuracy or a delayed independent re-audit.
6. **Why so many unknowns?** Only 44/700 critical claims were independently checked. Unsupported first-pass values were excluded from the active verified projection.
7. **Why preserve unknowns?** Missing evidence does not prove absence or buildability. Explicit uncertainty avoids giving reviewers unsupported connector decisions.
8. **How did you avoid leakage?** First-pass JSON and freeze hashes were retained; seed-42 sample definition preceded actual judgments; corrections and augmentation remain separately logged.
9. **Strongest patterns?** Permissions shape onboarding, OAuth lifecycle can be reusable, REST is common in checked API findings, MCP adds an execution surface, and buildability has conditions. These are bounded reviewed-subset observations, not prevalence estimates or category rankings.
10. **Another day?** Resolve unclear sampled identities/claims and expand independent field coverage with official sources; separately execute integrations and validate token lifecycle/permissions. Do not retroactively alter the baseline or sample denominator.
11. **End-to-end integrations?** None were executed. Documentation-based buildability is not integration-test proof.
12. **Reproduce?** Clone the Stage 05 branch, install requirements-stage02.txt, run README checks, inspect freezes/reviews/logs, and open the standalone HTML. No fresh API calls are necessary for checks.
13. **Why trustworthy despite incomplete coverage?** Original evidence is retained, outputs reproduce, checked claims have provenance, denominators and unresolved coverage are explicit, and the artifact makes no complete-row or whole-dataset accuracy claim.
