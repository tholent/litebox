# Oldest first ordering

2026-11-22 · untyped · 3 questions · lead: this session (Claude Opus 5.5), no workers

Chris's request, word for word: "bbq 3q oldest first ordering".

Where it stands before the change: setup's Order choice has two options, "Newest first" and "By folder and file
name" (`litebox.html:269-272`), saved inside `litebox.html` as `order: 'newest' | 'name'` (`litebox.html:321`,
`litebox.html:1084`). Loading stores the photos newest first, with photos taken at the same moment in name order
(`litebox.html:631`). The gallery reads the order through `ordered()` (`litebox.html:407`). Albums are always listed
by folder name, with Unsorted last (`litebox.html:415-416`).

## Rules

- **Q1 Where.** Setup only: a third choice in the Order list, in this order: Newest first / Oldest first / By folder
  and file name. It is saved in the file like the other settings. No button in the gallery.
- **Q2 Albums.** The album list stays in folder-name order whatever the Order choice. Oldest first orders only the
  photos inside each album and in "All photos" (and so the album covers, which follow the order).
- **Q3 Anything else.** Nothing else.

## Owed

Nothing owed.

## Defaulted

- **Label:** "Oldest first". veto: another wording.
- **Photos taken at the same moment** stay in name order A→Z in both Newest first and Oldest first, so it is not a
  plain flip of the list. veto: a plain flip (same-moment photos in Z→A order).
- **Photos with no date in them** use the file's date, as now. veto: none.
- **Files made before this change keep working** untouched: their saved order is `newest` or `name`, and anything
  unknown still falls back to Newest first. veto: none.
- **Tests:** Oldest first reorders an album straight away, ties stay A→Z, the album list does not move, the choice is
  saved in the file and read back. veto: fewer tests.
- **CHANGELOG** gets an Unreleased line. veto: none.

## Kickoff

Build these rules in `litebox.html`, add tests, a CHANGELOG line and a README mention if the README lists the Order
choices, run `python3 tests/run.py` and `ruff`/ESLint, and commit on `main` (no push without Chris). Lead: Claude
Opus 5.5 at its usual effort; a session on another model or effort stops and says so before doing anything.

## Built

2026-11-22, in the same session, committed on `main`: an "Oldest first" option in setup's Order list, a `byOldest`
sort with photos taken at the same moment kept in name order, and `orderOf` so an order litebox does not know falls
back to Newest first (`litebox.html`). README and CHANGELOG updated. Tests: `.venv/bin/python tests/run.py` gives
`litebox-tests: pass=164 fail=0` (155 before). `ruff check .` passes; `npx eslint .` reports errors only in
`samples/drive/.build/`, which git ignores and CI never sees. Not tested by a person yet: the new choice in a real
browser on the drive.

## Released

2026-11-22: in v0.3.0, tag `v0.3.0` on `2df2e90`, after Lint and Tests passed on that commit. Made as a draft,
its `litebox.html` checked against the repository's copy (sha256 `83114ddf…a1c4f7` both), then published on
Chris's word ("ok, let's push the commits, tag the release v0.3.0 and publish the release"). GitHub reports it
immutable.
