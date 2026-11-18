---
status: accepted
status-note: ratified by Chris on 2026-11-18
ratified-by: Chris
ratified-on: "2026-11-18"
owner: Chris
kind: process
built: landed
proof: AGENTS.md
supersedes: nothing
amends: nothing
---
# ADR-001 — Set litebox up for agents with the smallest set of pitmaster pieces, and add more only when needed

## Decision

litebox starts with the smallest pitmaster setup: one set of agent rules in `AGENTS.md` (with `CLAUDE.md` holding
only `@AGENTS.md`, so Claude Code loads the same rules) and a short `STATUS.md` whose every claim cites a file.
Three rule groups are on: Plan and decide, Check and review, and Plain words (catalogue 2026-10-23). Chris owns
taste, naming and decisions. The project has no doctrine yet; agents do not invent one. Decisions are recorded in
`docs/decisions/` in the ADR+ format. Other pieces (session log, debt list, archive, glossary, proposals,
`pitmaster.md` config) and other rule groups are switched on later, when a need shows up.

## Context

The repository was empty when this was decided: no commits on `main`, no remote. The setup was made with the
project-prep skill on 2026-11-18, taking its recommended answers: the smallest set of pieces and the three
pre-ticked rule groups. Chris's reason: start small, add later. Each rule is a line every agent reads every
session, so each costs a little context; turning on only what is needed keeps that cost low until the project
shows what it needs.

## Consequences

- Agents have one place for rules (`AGENTS.md`) and one for live state (`STATUS.md`).
- There is no separate session log or debt list yet; `STATUS.md`'s own Log and Known debt sections carry them.
- The Plain words rules mention a glossary, but there is no `docs/glossary.md` yet; adding it is a later choice.

## History

- 2026-11-18: drafted by makeadr (light route) from Chris's answers during project-prep.
- 2026-11-18: ratified by Chris ("ratify adr001"). Header before: `status: proposed`; `status-note: drafted 2026-11-18 from Chris's answers; awaiting ratification`.
