# Release prep — license, headers, README, CI

2026-11-18 · untyped · a request, not a numbered bbq · lead: this session (Claude Opus 5.5), no workers

## Chris's words

The request, word for word:

> let's do some legwork on this to make it ready for public release.
>
> * this project is licensed Apache-2. Please include the LICENSE file verbatim from here:
>   https://www.apache.org/licenses/LICENSE-2.0.txt
> * add appropriate apache-2 headers to the appropriate files
> * create a high-level user oriented README.md file for this project
> * setup github action workflows for linting and testing and place badges for each in the README.md file. the
>   workflows should using caching and shared setup where possible.
> * create a description text and tags for display on github. I will paste them in manually

## Rules

- **L1 License.** `LICENSE` is the Apache License 2.0 text downloaded from that address, unchanged (sha256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`).
- **L2 Headers.** Source files carry the Apache-2.0 header; `tests/check-headers.py` checks it.
- **L3 README.** `README.md` is written for the people who make and receive a litebox drive; developer notes
  come last.
- **L4 CI.** `.github/workflows/lint.yml` and `.github/workflows/test.yml`, sharing `.github/actions/setup`
  (Python with the pip cache; Node.js with the npm cache for lint). Badges for both lead the README.
- **L5 GitHub text.** A description and topics are given to Chris in the session, to paste into GitHub.

## Defaulted

- **Copyright holder "Chris Wells", year 2026**, from the git author name. veto: another name or wording.
- **Headers on code only:** `.html`, `.js`, `.mjs` and `.py` files. Not on Markdown, YAML, JSON, `LICENSE` or
  images. In `litebox.html` the header sits inside `<html>`, so the copy litebox saves of itself keeps it; a
  test checks that. veto: headers on more file types.
- **No `NOTICE` file:** Apache-2.0 needs one only to pass on notices; litebox bundles no one else's code.
  veto: add one.
- **Badges and links point at `github.com/cwlls/litebox`**, the signed-in GitHub account; that repository did not
  exist yet on 2026-11-18. veto: another owner or name. **Withdrawn 2026-11-18:** Chris named the remote: "the
  remote will be: github.com/tholent/litebox". The README now points there.
- **Lint:** ruff's default rules for Python; ESLint's recommended rules for JavaScript, including the script inside
  `litebox.html` through eslint-plugin-html, with unused `catch` names allowed; the license header check. veto:
  more or fewer rules, or ruff's formatter.
- **Versions pinned exactly** (`requirements-dev.txt`, `package.json`), current on 2026-11-18. There is no
  `package-lock.json` yet: this machine has no Node.js. veto: none; add the lock file once npm has run.
- **CI tests use the Chrome already on GitHub's Ubuntu machines**, with `--no-sandbox`, and keep the test drive as
  a download when a run fails. veto: install Chromium instead.
- **The logo in the README** swaps to `assets/logo-dark.png` (made by `assets/make-logo.py`) on GitHub's light
  theme, where the white logo would vanish. veto: one logo for both themes.
- **No screenshots in the README yet:** the test photos are plain coloured blocks. veto: add them anyway.

## Owed

- The linters have not been run: installing Node.js and ruff into the session's scratch folder was refused by the
  session's permission check. Run them locally, or let the first GitHub run show the results.
- Neither workflow has run: nothing has been pushed (push only with Chris's approval).
- Screenshots with real photos for the README, if Chris has some he is happy to publish.

## Remote

- 2026-11-18: Chris asked, word for word: "let's generate a deploy key and get this setup with the remote", then
  "the remote will be: github.com/tholent/litebox".
  - `tholent/litebox` already existed, empty and **public**. Chris has admin rights on it, but the signed-in token
    cannot manage deploy keys (HTTP 403), so Chris adds the key on GitHub's website.
  - Defaulted: **an ed25519 deploy key with no passphrase** on Chris's machine, with its own SSH host entry;
    `origin` pushes through it over SSH. veto: a passphrase, or HTTPS.
  - Not pushed: pushing waits for Chris's word, and the first push makes everything public.

## Release day (setfree)

- 2026-11-18: Chris typed "setitfree" and chose, through setfree's questions: "Push, then v0.1.0", run the blind
  tastetest first, and push the internal files "as they are".
- Blind tastetest on what the push would publish: **READY**, nothing blocking. Fixed from its list: the README
  now explains the browser's "edit files" / "upload" prompt on Load photos, the Space key, the **i** button and
  GitHub's "Download raw file" button, and says "made for" any modern browser; `tests/check-headers.py` works
  without git (a downloaded ZIP); the deploy-key note above no longer names local paths. Left open: the linters
  and workflows have not run, and nobody has tried a real USB stick on Windows or macOS.
- `CHANGELOG.md` added for 0.1.0.
- Pushed `main` on Chris's word ("Push main"). First runs: Tests passed; Lint failed on 13 ruff 0.17 findings in
  the Python test scripts (its default rules are broader than ruff's older ones). Fixed in `9a33f42` and pushed on
  Chris's word ("Push the fix"): Lint, including ESLint's first run, and Tests both pass.
- Chris asked, word for word, to add this badge to the README:
  `[![AI framework: pitmaster](https://img.shields.io/badge/AI_framework-pitmaster-yellow)](https://github.com/MapleSyrupOS/pitmaster)`
  (written as HTML to match the README's centred badge row).
- Chris's word on tagging: "Push first, then tag 80a986b", then "Push, then tag 872dd5e". Neither was tagged: Tests
  failed on GitHub both times. **Withdrawn: my "a bigger virtual-time budget fixes it" (872dd5e).** The cause was
  headless Chrome's simulated clock (`--virtual-time-budget`): on a busy machine it runs ahead of the page's real
  work, so a harness could be cut off (once after 1.8 real seconds, with 600 simulated ones spent). Reproduced here
  by loading all four cores. `tests/run.py` now runs each test page on a real clock and asks the page over
  Chrome's DevTools pipe whether its harness has finished: 10 runs out of 10 passed under load.
- Lint then failed once more on a misplaced `noqa` marker, fixed in `5a3e74a`. On Chris's word ("Push, then tag
  5a3e74a"), and after Lint and Tests both passed on it: **tag `v0.1.0` on `5a3e74a`, and the release "litebox
  0.1.0"** at https://github.com/tholent/litebox/releases/tag/v0.1.0, with the CHANGELOG's notes and `litebox.html`
  attached (60,037 bytes; the downloaded copy matches the repository's file).
- Chris turned on release immutability for `tholent/litebox` and asked whether the release steps need changing;
  then, to the offer of a written checklist: "yes, please". `docs/releasing.md` is that checklist, and
  `pitmaster.md` names it (`checklist:`) for setfree. Defaulted: **every release is made as a draft, checked, then
  published**, since a published release can no longer be fixed. veto: publish straight away, as v0.1.0 was.
  v0.1.0 itself was published before the setting and is not immutable (`isImmutable: false`).
