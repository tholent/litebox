# bbq — litebox's first working gallery

2026-11-18 · untyped · 12 questions · lead: this session (Claude Opus 5.5), no workers · no budget block

## Rules

- **Q1 Count.** 12 questions.
- **Q2 Scope.** The first piece of work is a first working gallery: the smallest litebox that opens from the
  thumbdrive and shows the photos.
- **Q3 Finding photos.** The photo list is built into the page and refreshed by a tool; the page never lists a
  folder on its own (a page opened from a drive is not allowed to).
- **Q4 Where it runs.** Any modern browser (Chrome, Edge, Firefox, Safari) on Windows, Mac and Linux, fully
  offline. No browser-only features unless there is a fallback for the rest.
- **Q5 Features.** A grid of photos plus a full-size viewer (click to open, arrow keys and swipe to step, Esc to
  close); captions and dates; the photo's EXIF description (ImageDescription tag); a slideshow. Not in: folders as
  albums.
- **Q6 Size.** Hundreds to a few thousand phone photos, 3–10 MB each, so the grid uses thumbnails.
- **Q7 Refresh tool.** The page refreshes itself: a Refresh button, the user picks the folder, litebox reads every
  photo and saves an updated `litebox.html`. On Chrome/Edge it overwrites itself; on Firefox/Safari it downloads the
  new file for the user to copy back onto the drive.
- **Q8 Thumbnails.** Made at refresh and packed inside `litebox.html` (about 10 KB each).
- **Q9 Formats.** Show JPEG, PNG, WebP, GIF and AVIF. Skip everything else (HEIC, videos, RAW) and have refresh
  report what it skipped.
- **Q10 Look.** Dark, photos first: near-black background, little chrome. (Taste: Chris's ruling.)
- **Q11 Layout.** `litebox.html` with a `photos` folder beside it. Only files inside `photos/` and its subfolders
  are included; everything else on the drive is ignored.
- **Q12 Protect.** litebox never modifies, moves or renames a photo; it only reads them. It never loads anything
  from the internet.

## Owed

Nothing owed.

## Defaulted

- **Dates and descriptions come from refresh.** Chrome will not let a page opened from a drive read a photo's
  bytes, so the date taken and the description are read at refresh (where the user's folder pick allows reading)
  and written into the built-in list. veto: none possible without dropping Q4's "any browser".
- **Order.** Newest first by date taken (EXIF DateTimeOriginal), falling back to the file's modified time.
  veto: oldest first, or by file name.
- **Caption.** Description first, then date taken, then the file name, smaller. veto: a different order or fewer
  fields.
- **Camera placeholder descriptions are hidden.** Descriptions some cameras fill in by themselves ("OLYMPUS
  DIGITAL CAMERA", "SONY DSC" and the like) are not shown. veto: show the tag exactly as stored.
- **Slideshow.** Starts from the viewer or a Play button, 5 seconds a photo, loops, Space pauses, Esc stops.
  veto: another interval or no loop.
- **Picking the folder.** Refresh asks for the folder that holds `litebox.html` (picking `photos` itself also
  works). Chrome/Edge use the folder picker that can write back; if it refuses (some drive roots), litebox falls
  back to the download route. veto: always download.
- **Tests.** `tests/` holds a script that makes test photos with Pillow (with EXIF dates, descriptions and a
  rotated photo) and drives headless Chromium through a refresh and the gallery, printing one structured result
  line. Firefox is checked by a headless screenshot; Safari and Windows are checked by Chris by hand.
  veto: a different split of what is automated.
- **System files are ignored, not reported.** Names starting with a dot (macOS `._` copies, `.DS_Store`, hidden
  folders), `Thumbs.db` and `desktop.ini` are left out silently. Added during the build. veto: report them too.
- **Viewer extras.** A click on the black around a photo closes the viewer; F toggles full screen. Added during
  the build. veto: drop either.
- **No outside code.** Everything (EXIF reading, thumbnails, the viewer) is written into `litebox.html` itself;
  no libraries, packed or linked. veto: allow a packed library for a named job.

## Overruled

None.

## Kickoff

Build litebox's first working gallery in this session, on `main`, from the rules above: one file,
`litebox.html`, that shows the photos in `photos/` beside it and refreshes its own built-in list and thumbnails,
plus `tests/` to prove it. Size: one session.

## Measured after the build

On this Raspberry Pi 5 in headless Chromium (2026-11-18): refresh read 150 photos of 4032x3024 (1.5 MB each) in
41 s, about 0.27 s a photo. Thumbnails came to about 14–16 KB each on these noisy test images, not the 10 KB Q8
guessed, so a 3,000-photo `litebox.html` is about 49 MB; it opened to a drawn grid in 3.7 s, against 2.4 s for an
empty litebox. A typical laptop should be several times faster; not measured.
