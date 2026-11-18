---
status: proposed
status-note: drafted 2026-11-18 from Chris's answers; awaiting ratification
owner: Chris
kind: process
built: landed
proof: docs/releasing.md
supersedes: nothing
amends: nothing
---
# ADR-002 — litebox releases are immutable, so each one is made as a draft on a commit whose checks passed, checked, and only then published

## Decision

Every litebox release on GitHub (`tholent/litebox`) is first made as a **draft**, pointing at a commit on `main`
where the Lint and Tests workflows both passed, with `litebox.html` attached. The draft is checked: its notes are
read, and the attached `litebox.html` is downloaded and compared with the repository's copy. Only then is it
published, on Chris's word. The steps are in `docs/releasing.md`, which `pitmaster.md` names as the release
checklist (`checklist:`) for the setfree skill.

## Context

Chris turned on release immutability for `tholent/litebox` on 2026-11-18, after v0.1.0 was published. With it on,
a published release's tag cannot be moved or deleted, and its attached files cannot be replaced or removed (`gh`
2.103's help for `gh release create`, read 2026-11-18). Chris's reason for this decision: **mistakes are
permanent**. A published release can only be fixed by making a new version, so a mistake has to be caught while
the release is still a draft, which can still be edited or deleted.

v0.1.0 was published straight away, without a draft, and before immutability was on; GitHub reports it as not
immutable (`isImmutable: false`). Its history, including two failed test runs that held back its tag, is in
`docs/bbq/2026-11-18-release-prep.md`.

## Consequences

- Each release takes one more step than v0.1.0 did (create the draft, check it, publish it), and one more stop for
  Chris's word: the publish, beside the push.
- A wrong file or a wrong commit can still be fixed before publishing. After it, the fix is a new version
  (0.1.0 → 0.1.1).
- `docs/releasing.md` has not been followed end to end yet: the next release is its first use.

## History

- 2026-11-18: drafted by makeadr (light route) from Chris's answers ("Use my draft", "Mistakes are permanent",
  "Landed in docs/releasing.md"), after Chris asked for the checklist ("yes, please").
