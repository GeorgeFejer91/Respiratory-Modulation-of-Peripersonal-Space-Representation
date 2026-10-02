# Decision log

Record only durable choices whose rationale future agents would otherwise have
to rediscover. Source and tests remain the authority for implementation facts.

## D-0001 — Minimal control plane before product scaffolding

- Date: 2026-10-02
- Status: Accepted
- Context: The project needs a predictable AI entrypoint without choosing an
  application stack or inventing product structure prematurely.
- Decision: Use a short root `AGENTS.md` that routes to a lowercase `for-ai/`
  control plane. Keep product output outside that folder and add project files,
  skills, and protocols only for current requirements.
- Consequences: New agents get a reliable map and readiness gates. The first
  product task must still choose the smallest suitable output structure.
- Supersedes: None

## Record format

For later decisions, add one compact entry with:

- identifier and title;
- date and status (`Proposed`, `Accepted`, `Superseded`, or `Rejected`);
- context;
- decision;
- consequences;
- supersession link when applicable.

Do not rewrite accepted history to hide a changed direction. Add a superseding
decision and link both entries.

## D-0002 — Private unified publication candidate

- Date: 2026-10-02
- Status: Accepted
- Context: The cleared export includes 42 independent people and a separate
  private identity/provenance archive.
- Decision: Publish only deidentified primary behavioral rows in this private
  repository, renumbered contiguously from `P000` to `P041`. Keep the source
  crosswalk and raw recordings outside it; require an ethics and consent review
  before any public visibility change.
- Consequences: One person key joins the two CSVs. The private source archive
  remains necessary for provenance audits and any future source correction.
- Supersedes: None

## D-0003 — Preserve the earlier manuscript as a draft

- Date: 2026-10-02
- Status: Accepted
- Context: The active manuscript reports 40 people, while the current
  publication-data candidate contains 42.
- Decision: Keep the complete existing preprint and referenced figures
  available for writing, but do not relabel its estimates as 42-person results.
  Promote analyses only after a reproducible rerun and review.
- Consequences: The Overleaf project compiles, but the scientific submission
  gate remains open until the text, tables, and figures are refreshed.
- Supersedes: None
