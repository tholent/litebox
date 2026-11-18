# Releasing litebox

The steps for making a release, in order. The `setfree` skill reads this file (`checklist:` in `pitmaster.md`).
Decided by `docs/decisions/ADR-002-make-each-release-as-a-checked-draft-before-publishing.md`.

**Releases are permanent.** Release immutability is on for `tholent/litebox`: once a release is published, its
tag cannot be moved or deleted, and its attached `litebox.html` cannot be replaced or removed. A mistake in a
published release is fixed by a new release (0.1.0 → 0.1.1), never by editing the old one. A **draft** release
can still be changed freely, so every release is checked as a draft before it is published.

Steps marked **(Chris's word)** are public acts: an agent stops and asks before each one.

## 1. Choose the version

Chris names the version number. As a guide: a fix only → the last number goes up (0.1.0 → 0.1.1); new
features → the middle number goes up and the last returns to 0 (0.1.1 → 0.2.0).

Below, `X.Y.Z` stands for that number.

## 2. Start from an up-to-date, clean `main`

```sh
git switch main
git pull --ff-only
git status --short          # must print nothing
```

## 3. Run the checks locally

```sh
python3 tests/run.py        # last line must read fail=0
python3 tests/check-headers.py
```

## 4. Update the changelog

Add a section at the top of `CHANGELOG.md`, below its introduction, written for the people who use litebox:

```markdown
## X.Y.Z — YYYY-MM-DD

- What changed, in plain words.
```

Commit it on `main`: `git commit -am "CHANGELOG: X.Y.Z"`.

## 5. Push, and wait for both workflows to pass **(Chris's word for the push)**

```sh
git push
gh run list -R tholent/litebox --limit 2 --json workflowName,conclusion,headSha
```

Both `Lint` and `Tests` must show `success` for the commit just pushed (`git rev-parse HEAD`). If either fails,
fix it, push again, and wait again. Never release a commit whose checks did not pass.

## 6. Write the release notes

The changelog section, followed by a short "Getting started" paragraph:

```sh
awk '/^## X\.Y\.Z /{f=1; next} /^## /{f=0} f' CHANGELOG.md > /tmp/litebox-notes.md
cat >> /tmp/litebox-notes.md <<'NOTES'

### Getting started

Download `litebox.html` below, put it on a drive next to a folder called `photos`, open it in your browser and
click **Set up litebox**. The [README](https://github.com/tholent/litebox#make-a-litebox-drive) walks through
every step.

### Checking your download

This release is immutable: its `litebox.html` can never be swapped. To confirm a downloaded copy is the one
published here, run `gh release verify-asset vX.Y.Z litebox.html -R tholent/litebox` (GitHub CLI).
NOTES
```

## 7. Create the release as a draft

The draft points at the exact commit that passed in step 5. The tag is not made until the draft is published.

```sh
gh release create vX.Y.Z litebox.html -R tholent/litebox --draft \
  --target "$(git rev-parse HEAD)" --title "litebox X.Y.Z" --notes-file /tmp/litebox-notes.md
```

Then check the draft:

- Open it on GitHub (`gh release view vX.Y.Z -R tholent/litebox --web`) and read the notes.
- Confirm the attached file is the repository's own:

  ```sh
  mkdir -p /tmp/litebox-check && rm -f /tmp/litebox-check/litebox.html
  gh release download vX.Y.Z -R tholent/litebox -p litebox.html -D /tmp/litebox-check
  sha256sum /tmp/litebox-check/litebox.html litebox.html     # the two sums must match
  ```

Anything wrong is fixed now, while it is still a draft: `gh release edit` for the notes or title,
`gh release upload vX.Y.Z litebox.html --clobber` for the file, or `gh release delete vX.Y.Z` to start again.

## 8. Publish **(Chris's word)**

```sh
gh release edit vX.Y.Z -R tholent/litebox --draft=false
```

From here the tag and `litebox.html` are permanent.

## 9. Check the published release

```sh
gh release view vX.Y.Z -R tholent/litebox --json isImmutable,isDraft,tagName   # isImmutable: true
gh release verify vX.Y.Z -R tholent/litebox                                      # GitHub's attestation
```

Anyone can check a downloaded copy the same way: `gh release verify-asset vX.Y.Z litebox.html -R tholent/litebox`.

## 10. Record it

- `STATUS.md`: the release under Now, and any follow-up under Next.
- The session's record in `docs/bbq/`, if the release came out of one.
