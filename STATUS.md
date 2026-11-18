# STATUS — litebox

_Last updated: 2026-11-18_

The project's live state. Update it when work lands. Every claim cites at least one file that exists.

## Now

- Project prepared for agents with project-prep: the rules are in `AGENTS.md`.
- First decision ratified: the smallest agent setup (`docs/decisions/ADR-001-set-up-litebox-with-the-smallest-agent-setup.md`).
- First working gallery built to the bbq's rules: grid, viewer, captions with EXIF date and description, slideshow, and a Refresh that rebuilds the file's own photo list and thumbnails (`litebox.html`, `docs/bbq/2026-11-18-first-working-gallery.md`).
- Second round built: albums from top-level folders (album grid first), search, optional dates, footer line, slideshow speed slider, an EXIF details panel, and setup with Refresh hidden behind `#setup` (`litebox.html`, `docs/bbq/2026-11-18-second-round.md`).
- Logo in the header bar and as the tab icon, embedded in the page; a Header text setting in setup (`assets/logo.png`, `docs/bbq/2026-11-18-second-round.md`).
- Setup reworked: "Load photos" / "Update photos" only reads them and shows a green check with the time; litebox.html is saved or downloaded only by its own button, and closing setup or the tab with anything unsaved warns first (`litebox.html`, `docs/bbq/2026-11-18-second-round.md`).
- Release prep: Apache-2.0 `LICENSE`, license headers, a user-facing README, and GitHub workflows for lint and tests with shared setup and caching (`README.md`, `.github/workflows/lint.yml`, `.github/workflows/test.yml`, `docs/bbq/2026-11-18-release-prep.md`).
- **v0.1.0 released** on 2026-11-18: tag `v0.1.0` on `5a3e74a`, with `litebox.html` attached (`CHANGELOG.md`).
- Pushed to github.com/tholent/litebox on 2026-11-18; Lint (ruff, ESLint, license headers) and Tests pass there, with the pip and npm caches in use (`.github/workflows/lint.yml`, `.github/workflows/test.yml`).
- Automated tests pass in headless Chromium, on a real clock: 144 checks, run with `python3 tests/run.py` (`tests/run.py`).

## Next

- Chris to rule on ADR-002, draft-first releases (proposed) (`docs/decisions/ADR-002-make-each-release-as-a-checked-draft-before-publishing.md`).
- Try v0.1.0 on a real USB stick on Windows and macOS (Chrome and Safari), the one check the blind review asked for that no test covers (`docs/bbq/2026-11-18-release-prep.md`).
- Chris to try the second round on the 231 real images: open `litebox.html#setup`, Load photos, set the header text, footer and dates, Download, then view it as a recipient would (`litebox.html`).

## Known debt

- The folder pickers and saving in place (Chrome, Edge) are not covered by the automated tests; they need a person to click. The download route is tested by catching the download (`tests/harness1.js`).
- Refresh speed measured only on this Raspberry Pi 5: about 0.27 s per 12-megapixel photo, so about 14 minutes for 3,000; a 3,000-photo file is about 49 MB (`docs/bbq/2026-11-18-first-working-gallery.md`).
- The Plain words rules offer to file terms in a glossary, but `docs/glossary.md` does not exist yet (`AGENTS.md`).

## Log

- 2026-11-18: prepared with project-prep; ADR-001 drafted with makeadr and ratified by Chris; first working gallery planned with bbq and built; second round (albums, search, hidden setup, details panel) built; logo and header text added; header-text save bug fixed; setup reworked so only its save button saves. Release prep (license, headers, README, CI), pushed to GitHub, v0.1.0 released.

## How this file is kept

Live state stays here: what works now, what is next, and the top of the debt list. Every bullet under Now, Next
and Known debt cites at least one file that exists. Keep this file under 300 lines; the project-prep
skill's `scripts/status-check.py` checks both.
