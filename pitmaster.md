# pitmaster settings — litebox

Every pitmaster skill reads its `key: value` lines from here; a line here wins over the skill's own default.
Every line is optional. Each skill's Config section lists the keys it reads.

All work is committed straight to `main`, with no feature branches or pull requests (Chris, 2026-11-18; see
"Ground rules" in `AGENTS.md`). Where a skill's `land: commit` means "commit on a branch", the main branch is that
branch.

```
name: Chris
status_ceiling: 300
branch: main
land: commit
checklist: docs/releasing.md
```
