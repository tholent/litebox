# Download button — cancelled

2026-11-22 · untyped · 4 questions asked, then 4 owed asked · lead: this session (Claude Opus 5.5), no workers

**Cancelled by Chris before any build.** His words, word for word: "let's cancel this request. the browser
limitations make this not work well for me".

## Why: what the browser allows

Measured on 2026-11-22 in Chromium 156 (headless, on this Raspberry Pi), a page opened from the drive, without the
`--allow-file-access-from-files` flag the tests use (`tests/run.py:163`). The probes were throwaway scripts in the
session's scratch folder, not kept.

| What the page tries | Normal browser | With the test flag |
|---|---|---|
| Show a photo from `photos/` on screen | works | works |
| Copy the shown photo into a file (canvas) | `SecurityError` | works |
| Read the photo file (`fetch`) | `Failed to fetch` | works |
| A link to the photo marked "download" | opens the photo in the gallery's tab, no download | — |

So a page opened from the drive can show the full photos but cannot read them, and cannot make the browser download
them. `litebox.html` itself holds only 240-pixel square thumbnails (`litebox.html:313`, `litebox.html:580-584`); the
full photos stay in `photos/` and the viewer shows them by their place on the drive (`litebox.html:840`).

Not measured: whether a file the page builds itself downloads from a page opened from the drive. The probe caught no
download even from an ordinary web page, so that probe, not the browser, was at fault.

## Answers given before the cancel

These stand only as a record of what was asked; nothing was built.

- **Q1 Action.** Chris: "I'm looking for something that would allow multiselect from the gallery page and then a
  single download button". (The recommendation, open the photo in a new tab, was overruled.)
- **Q2 Where.** Viewer only. Replaced by Q5 once Q1 asked for multi-select.
- **Q3 Setting.** A setup check box, on by default.
- **Q4 Anything else.** Nothing else.
- **Q5 Where.** Gallery multi-select plus a button in the viewer.
- **Q6 Getting the full photos.** Asked three times. Chris: "The photos will already have been read and loaded into
  the html when this site is presented to them frmo the thumbdrive"; then "on the viewer, when an image is clicked
  a full view is displayed. Isn't that representative of the html file displaying the actual file on disk?"; then
  the cancel above. The routes offered: the viewer picks the drive's `photos` folder once a visit (recommended),
  opening each photo in its own tab, or carrying a download copy of each photo inside `litebox.html` (about 1.2 GB
  for 3,000 photos).
- **Q7 Result.** One zip for two or more photos, a single photo as is.
- **Q8 Selecting.** A "Select" mode with check boxes.

## Owed

Nothing owed: the request is cancelled.

## If it comes back

Start from the table above. The routes that work are the folder picker (one click a visit for the viewer) or
carrying copies inside `litebox.html`; Chris found neither good enough on 2026-11-22.
