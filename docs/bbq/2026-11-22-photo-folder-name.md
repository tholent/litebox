# Photo folder of any name

2026-11-22 · untyped · 4 questions · lead: this session (Claude Opus 5.5), no workers

Chris's request, word for word: "Can we make the 'photos/' whatever folder the user first selects on litebox setup?"

Where it stands before the change: setup accepts only a folder called `photos`, or a folder that holds one
(`litebox.html:646-652` for Firefox and Safari, `litebox.html:1170-1176` for Chrome and Edge). After loading, the
gallery keeps each photo's path, such as `photos/Holiday 2024/IMG_01.jpg`, finds it next to `litebox.html`
(`litebox.html:840`), and takes albums from the second part of the path, whatever the first is called
(`litebox.html:397-400`).

The limit: the browser tells the page the chosen folder's name and contents, never where it sits. The gallery looks
for photos next to `litebox.html`, so the folder may have any name but must sit next to `litebox.html` on the drive.

## Rules

- **R0 Any name.** The folder chosen in setup is the photo folder, whatever it is called. Its name becomes the first
  part of each photo's path, as `photos` does now.
- **Q1 Choosing the drive.** When the folder chosen is the drive itself (it holds `litebox.html`): if one folder on
  it holds photos, use that folder; if several do, list them and ask which.
- **Q2 Check and warn.** After loading, setup tries to show one loaded photo from where `litebox.html` is. If it
  cannot, it says in plain words that litebox can't see these photos from here, and that the folder must sit next to
  `litebox.html` on the drive. Showing a photo from the drive is allowed in a normal browser; reading it is not
  (measured 2026-11-22, `docs/bbq/2026-11-22-download-button.md`), so the check shows, never reads.
- **Q3 Wording.** The empty page and the README still suggest `photos/` in their picture, with one line: any name
  works, as long as the folder sits next to `litebox.html`.
- **Q4 Anything else.** Nothing else.

## Owed

Nothing owed.

## Defaulted

- **A folder "holds photos"** when it has at least one file a browser can show, at any depth. Hidden and system
  folders are skipped, as now. veto: count any file.
- **Several folders hold photos, one called `photos`:** still ask; no folder wins by its name. veto: pick `photos`
  without asking, as today.
- **Photos lying loose on the drive next to `litebox.html`** are not offered when the drive is chosen. veto: offer
  "the whole drive" as one more choice.
- **The check's warning also covers setting up from a copy** of `litebox.html` that is not on the drive yet: it says
  the check passes once the file and folder are on the drive together. veto: no check unless opened from the drive.
- **Files made before this change keep working** untouched: their paths already start with `photos/`. veto: none.
- **Tests:** a drive whose photo folder has another name; a drive with two photo folders (the choice is asked); the
  check's warning when the photos are not next to `litebox.html`. The check uses a shown photo, so it works without
  the tests' file-access flag. veto: fewer tests.
- **CHANGELOG** gets an Unreleased line. veto: none.

## Kickoff

Build these rules in `litebox.html`, update the empty page, README, tests and CHANGELOG, run
`python3 tests/run.py` and `ruff`/ESLint, and commit on `main` (no push without Chris). Lead: Claude Opus 5.5 at its
usual effort; a session on another model or effort stops and says so before doing anything.
