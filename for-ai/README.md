# Respiratory Modulation of Peripersonal Space Representation agent control plane

Read this file first. It is a router, not the complete project manual.

## Purpose

`for-ai/` separates AI orchestration from product output. Store durable project
context, skill routing, decisions, verification rules, and agent workflows
here. Keep product source, shipped assets, end-user documentation, and final
deliverables outside this directory.

GitHub Pages is now the intended primary analysis workspace and living preprint.
Use `PROJECT.md` for that contract and `ANALYSIS_ROADMAP.md` for the migration and
publication-readiness checklist; hosting and skill setup do not establish readiness.

## Authority order

1. System, developer, and current user instructions.
2. Applicable law, safety, privacy, and external contracts.
3. This repository's verified source, tests, schemas, and configuration.
4. Current canonical documents in `for-ai/`.
5. Historical decisions and external references.

If authorities disagree, stop and surface the conflict. Do not silently choose
the easiest interpretation.

## Read by task

| Need | Read |
| --- | --- |
| Scope, goals, boundaries, architecture, current state | [`PROJECT.md`](./PROJECT.md) |
| Results-first questions, ordered checklist and progress | [`ANALYSIS_ROADMAP.md`](./ANALYSIS_ROADMAP.md) |
| Which installed skills apply and in what order | [`SKILLS.md`](./SKILLS.md) |
| Structure a live paper, explain preprocessing or assess multiverse templates | [`LIVE_PAPER_REFERENCES.md`](./LIVE_PAPER_REFERENCES.md) |
| Choose a scientific web plot, library, SVG schematic or worked example | [`visualization/README.md`](./visualization/README.md), then only the selected toolkit profile |
| Acceptance criteria, commands, gates, evidence limits | [`VERIFICATION.md`](./VERIFICATION.md) |
| Session loop, updates, Git publication, handoff | [`WORKFLOW.md`](./WORKFLOW.md) |
| Why a durable choice was made or superseded | [`DECISIONS.md`](./DECISIONS.md) |
| Rebuild or check publication CSVs; stage exploratory analyses | [`orchestration/README.md`](./orchestration/README.md) |
| Compare prior manuscript versions | [`writing-archive/README.md`](./writing-archive/README.md) |

Do not read every file by default. Read this router, then only what the current
task touches.

## Session loop

1. Resolve the repository root and inspect Git status before changing anything.
2. State the requested observable outcome and select the task-owned documents,
   skills, and verification gates.
3. Inspect the existing owner before adding code, files, dependencies, or
   abstractions.
4. Make the smallest complete change and preserve unrelated work.
5. Run focused checks, then proportionate integration and publication gates.
6. Update the narrowest canonical control-plane file when a durable fact
   changed.
7. Report evidence, limitations, commit/remote state, and any blocker.

Standing owner authorization: use the Superpowers Git completion flow to
automatically commit and push validated task-owned changes and publish live-page
updates. Follow [`WORKFLOW.md`](WORKFLOW.md#git-checkpoints-and-publication) for
verification, integration, deployment checks and external blockers; do not ask
again for routine publication already covered by this instruction.

## Publication boundary

The project owner authorised public repository visibility on 2026-10-16,
superseding the earlier source-private restriction; see D-0011 in `DECISIONS.md`.
The owner previously authorised public release of the audited deidentified CSV
pair and confirmed ethical approval; see `workbook/DATA_RELEASE.md`.
The Pages artifact contains the browser companion,
that dataset and reproducible publication-draft materials. Author review before
paper submission and successful Pages deployment remain separate gates. Private
backups, identity/provenance archives and raw recordings stay outside deployment.

<!-- rtk-workflow -->
## Shell output

Prefer supported RTK filters for human-read shell output; see the [RTK skill](skills/rtk/SKILL.md). Keep exact reads and parser input raw. Use bounded native commands when RTK is unavailable.
<!-- for-ai-coding-workflows-route:start -->
## Skill routing

Use [`SKILLS.md`](./SKILLS.md) for task-specific skill selection. Coding work can load one matching nested workflow guide: [focused changes](./skills/superpowers-workflow/SKILL.md) or [multi-phase work](./skills/gsd-core-workflow/SKILL.md).
<!-- for-ai-coding-workflows-route:end -->
