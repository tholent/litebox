# STATUS — litebox

_Last updated: 2026-11-18_

The project's live state. Update it when work lands. Every claim cites at least one file that exists.

## Now

- Project prepared for agents with project-prep: the rules are in `AGENTS.md`.
- First decision ratified: the smallest agent setup (`docs/decisions/ADR-001-set-up-litebox-with-the-smallest-agent-setup.md`).
- First working gallery built to the bbq's rules: grid, viewer, captions with EXIF date and description, slideshow, and a Refresh that rebuilds the file's own photo list and thumbnails (`litebox.html`, `docs/bbq/2026-11-18-first-working-gallery.md`).
- Second round built: albums from top-level folders (album grid first), search, optional dates, footer line, slideshow speed slider, an EXIF details panel, and setup with Refresh hidden behind `#setup` (`litebox.html`, `docs/bbq/2026-11-18-second-round.md`).
- Logo in the header bar and as the tab icon, embedded in the page; a Header text setting in setup (`assets/logo.png`, `docs/bbq/2026-11-18-second-round.md`).
- Automated tests pass in headless Chromium: 113 checks, run with `python3 tests/run.py` (`tests/run.py`).

## Next

- Chris to try the second round on the 231 real images: open `litebox.html#setup`, Refresh, set the header text, footer and dates, Save, then view it as a recipient would (`litebox.html`).

## Known debt

- The folder pickers, saving in place (Refresh and Save settings) and the download route are not covered by the automated tests; they need a person to click (`tests/run.py`).
- Refresh speed measured only on this Raspberry Pi 5: about 0.27 s per 12-megapixel photo, so about 14 minutes for 3,000; a 3,000-photo file is about 49 MB (`docs/bbq/2026-11-18-first-working-gallery.md`).
- The Plain words rules offer to file terms in a glossary, but `docs/glossary.md` does not exist yet (`AGENTS.md`).

## Log

- 2026-11-18: prepared with project-prep; ADR-001 drafted with makeadr and ratified by Chris; first working gallery planned with bbq and built; second round (albums, search, hidden setup, details panel) built.

## How this file is kept

Live state stays here: what works now, what is next, and the top of the debt list. Every bullet under Now, Next
and Known debt cites at least one file that exists. Keep this file under 300 lines; the project-prep
skill's `scripts/status-check.py` checks both.
