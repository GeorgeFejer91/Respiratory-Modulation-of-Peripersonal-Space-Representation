# Agent workflow, context maintenance, and Git policy

## Working loop

1. Read `AGENTS.md`, then the router and task-owned files.
2. Inspect Git status, branch, remotes, relevant code, tests, and recent history.
3. Preserve user work and distinguish pre-existing failures from regressions.
4. Apply YAGNI: check the existing owner before adding anything.
5. Implement one bounded outcome and verify it proportionately.
6. Review the diff for accidental scope, secrets, generated output, and stale
   context.
7. Update project memory and publish only when the rules below apply.

## Control-plane update triggers

Update the narrowest canonical file in the same change when any durable fact
changes:

- project goal, non-goal, user workflow, or supported surface;
- module ownership, architecture boundary, external contract, or schema;
- required skill route or verified fallback;
- acceptance criterion, validation command, evidence limit, or release gate;
- security, privacy, safety, licensing, or publication boundary;
- durable decision or repeatedly rediscovered failure mode.

Do not store chat transcripts, daily narration, raw logs, transient branch
names, private machine paths, speculative ideas, secrets, participant data, or
facts already obvious from source and tests.

## Analysis promotion

GitHub Pages is the primary current publication and analysis workspace (D-0015).
Author its HTML narrative from verified outputs while retaining the version-1.9
manuscript/reference as a historical snapshot. The earlier results-only phase
(D-0012) remains the provenance of its outputs, not a continuing ban on HTML paper
authoring. Promote independently hashed Bayesian browser downloads to
`results/bayesian/` only after `validate_bayesian.py` checks. Update the results
report and roadmap; do not invoke the legacy manuscript-promotion script merely
to update the living paper. Keep both reference identities distinct.

An exploratory browser session is not automatically the published analysis.
Capture its input hashes, code revision, settings/formulas, cohort, exclusions,
seed, versions, result hashes and uncertainty/diagnostics in a downloadable run
record. Paper figures and claims must identify the approved record they use.
Native-only work stays explicitly labelled until browser execution, download and
independent numerical comparison pass. The roadmap owns this migration by method.

Keep the current living page and immutable publication versions distinct. Before
declaring a publication-ready release, record the source commit/version, analysis
manifest, data and figure downloads, references, author/scientific review and the
observed deployment. Preserve a citable Git tag/release or archived snapshot for
each released version; do not invent a DOI, peer-review status or archival deposit.

The browser publication pipeline is explicitly authorised by the project owner.
Its estimands, cohort, cleaning and registration interpretations are recorded in
`workbook/ANALYSIS_PLAN.md`. Keep historical source analyses in orchestration;
maintain the executable browser engine in `workbook/`. For legacy manuscript
promotion, use verified actual browser downloads with
`analysis/prepare_publication.py`, then reconcile manuscript
claims and preserve older prose in `writing-archive/`.

The export must remain free of private crosswalks and source paths. Owner data-release
authorisation and ethical approval are recorded in DATA_RELEASE.md; no further
release confirmation is needed for this exact audited dataset. A refresh requires
a new field audit and verified private backup. Submission readiness still requires
author review of scientific interpretations and missing provenance.

## Git checkpoints and publication

Owner standing instruction (2026-10-22): automatically complete the Superpowers
Git flow for every authorized repository change, including protocol/documentation
changes. This is continuing authorization to commit and push validated task-owned
work and publish live-page changes; do not ask again for routine commits, pushes
or permitted integration. The rule persists across sessions until the owner changes it.

Owner reaffirmation (2026-10-23): keep completed work pushed regularly. The active
Codex hourly follow-up checks this repository and its worktrees, commits and pushes
verified public-safe work, and preserves historical branch checkpoints without
automatically merging them. Keep ignored/private material excluded and unfinished
concurrent edits intact. Verify remote SHAs; report meaningful pushes or blockers.

Use the installed Superpowers verification/branch-finishing skills when present;
otherwise use the reviewed local
[`superpowers-workflow`](skills/superpowers-workflow/SKILL.md) guide with this
project-specific completion sequence. Do not claim upstream skills ran when absent.

1. Inspect status, branch, upstream and worktrees; isolate work when needed and
   preserve unrelated changes. Use the existing roadmap as the goal/state owner.
2. Run applicable `VERIFICATION.md` gates and review the complete task diff.
   Fix regressions before publication; checkpoint only coherent task-owned changes.
3. Stage explicit paths and create descriptive Git commits automatically. Commit
   durable protocol/evidence updates as part of the task; do not sweep in unrelated
   files, caches, private inputs or another task's unfinished work.
4. Fetch and integrate current remote changes without rewriting shared history.
   Push promptly and integrate into `main` using the permitted normal fast-forward,
   merge or PR path. Respect branch protection; resolve ordinary conflicts within
   scope and rerun affected checks. Create/attach a PR when the required path uses one.
5. For live-page changes, follow the exact source SHA through the existing Pages
   workflow, CI and deployment, then exercise the changed live behavior. A source
   push, successful build and successful live deployment are separate observations.
   Protocol-only commits need their context/link/diff checks and remote-SHA check;
   do not trigger a redundant site build when the served artifact is unchanged.
6. Record observed evidence, commit/remote/publication state, blockers and the next
   action in `ANALYSIS_ROADMAP.md`. If an external gate prevents completion, retain
   the ready commit, identify the exact gate and resume its verification at the next
   task entry. Ask only for genuinely missing information or an external action
   that cannot be completed under the standing authorization.

- Never force-push, rewrite shared history, bypass branch protection, bypass
  secret scanning, or publish known-broken/private material.
- Read-only review does not authorize changing or publishing unrelated work.

## Self-review

Run `for-ai/scripts/check-context.ps1`. Then review control-plane changes for
contradictions, duplication, stale facts, oversized always-read material, and
rules that lack a current consumer. Consolidate or delete rather than append
forever.

## Itemized handoff

- Outcome and affected product surfaces.
- Intended files changed; unrelated work left untouched.
- Verification run, result, and evidence limitations.
- `for-ai/` update: yes/no and why.
- Commit SHA, branch, remote sync, CI/deployment result.
- Remaining blocker or next smallest product decision.
