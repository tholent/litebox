# Changelog

What changed in each release of litebox. Dates are the day the release was made.

## Unreleased

- Setup has an **Order** choice: newest first, as before, or by folder and file name, which suits scans whose
  dates mean nothing. It is saved inside `litebox.html` with the other settings.
- The photo folder can have **any name**, not only `photos`, as long as it sits next to `litebox.html`. When the
  drive itself is chosen and more than one folder on it has photos, setup asks which one. Setup warns when it
  can't see the loaded photos from where `litebox.html` is. Files set up before keep working.

## 0.1.0 — 2026-11-18

The first release.

### What litebox does

- A photo gallery in one file, `litebox.html`, that sits on a drive beside a `photos` folder and opens in any
  modern browser (Chrome, Edge, Firefox, Safari) on Windows, Mac and Linux, with no internet connection.
- Albums from the folders inside `photos`, opening on an album grid; photos outside any folder go in "Unsorted".
- A grid of small previews stored inside `litebox.html`, and a full-screen viewer with arrow keys, swipe and
  full screen.
- A slideshow with a speed slider.
- Captions from each photo's own description and date (its EXIF data); dates can be hidden.
- A details panel: camera or scanner, lens, exposure, resolution, artist and copyright.
- Search across descriptions, file names and album names.
- A setup page, hidden from the people viewing the photos, for loading the photos and setting the header text,
  footer line, dates and slideshow speed. Chrome and Edge save `litebox.html` onto the drive; Firefox and Safari
  download it for you to copy back.
- litebox only reads photos: it never changes, moves or renames them, and never connects to the internet.
