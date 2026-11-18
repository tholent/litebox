# Second round — albums, search, hidden setup, info panel

2026-11-18 · untyped · discussion, not a numbered bbq · lead: this session (Claude Opus 5.5), no workers

Follows `docs/bbq/2026-11-18-first-working-gallery.md`. Chris tried the first gallery with 231 real images ("it
works mostly as expected") and asked for these changes.

## Chris's words

The request, word for word:

> - search box (searches descriptions/titles/tags)
> - display of folders (1 level ) as albums
> - make capture date display optional (these are mostly scans and the capture date is meaningless)
> - custom footer line
> - slideshow adjust time slider
> - info panel on picture (toggle to show exif info)
> - refresh button on footer bar (refresh is only really used to create the thumbdrive and then hidden)
> - "changed on disk" badge for images that changed on disk since a refresh

The rulings on the open questions, word for word:

> 1. let's drop the titles and tags bit
> 2. unsorted is good. album grid for initial view
> 3. Let's put refresh in the settings tab, but we also need to make the settings kind of hidden so that endusers
>    don't use it. this software is meant to be setup by someone and then just viewed by the recipient. I don't
>    want anyone monkeying around with the settings after the initial load
> 4. drop it

## Rules

- **R1 Search.** A search box filters photos as you type, by description. No titles or tags (ruling 1).
- **R2 Albums.** Each top-level folder in `photos/` is an album; deeper folders roll up into it. Photos directly in
  `photos/` go in an album called "Unsorted". The opening view is the album grid (ruling 2). This reverses the
  first round's Q5 ("Not in: folders as albums").
- **R3 Dates optional.** A setting hides the date in captions and the info panel.
- **R4 Footer line.** A setting holds one line of text shown in a footer bar.
- **R5 Slideshow speed.** A slider in the viewer sets the seconds per photo while the slideshow runs.
- **R6 Info panel.** A toggle in the viewer shows the photo's EXIF details, read at refresh.
- **R7 Setup is hidden.** Refresh lives in the settings, and the settings are hidden from the people who view the
  gallery: litebox is set up by one person and then only viewed by the recipient (ruling 3).
- **R8 No changed-on-disk badge** (ruling 4).

## Defaulted

- **Setup is reached by adding `#setup` to the address.** No button for it shows anywhere, except on a new litebox
  with no photos yet, whose empty page offers "Set up litebox" to the person setting it up. This keeps out casual
  clicking, not a determined person: anyone can edit the file in a text editor. veto: a key combination instead.
- **Settings are saved inside `litebox.html`**, beside the photo list, the same way Refresh saves (in place on
  Chrome/Edge, by download elsewhere). veto: none without a second file on the drive.
- **Search also matches file names and album names**, and searches the album you are in, or every photo from the
  album grid. veto: descriptions only.
- **No subfolders at all:** the album grid is skipped and the photos show straight away. veto: always show the
  album grid, even with only "Unsorted".
- **An "All photos" tile comes first in the album grid.** Added during the build. veto: drop it.
- **The speed slider shows only while the slideshow plays.** Added during the build. veto: always show it.
- **Albums are sorted by name** (numbers in order: "2" before "10"), "Unsorted" last; each album's cover is its
  newest photo. veto: another order or cover.
- **"Hide dates" hides both the date taken and the file date.** veto: hide only the date taken.
- **Slider range 2–20 seconds**, starting at the setting's default (5 s); each viewer's browser remembers its last
  choice. veto: another range, or no remembering.
- **Info panel fields:** file name, album, pixel size, file size, camera or scanner make and model, lens, exposure,
  aperture, ISO, focal length, resolution (DPI), software, artist, copyright, and the date unless dates are hidden.
  Toggled with an ⓘ button or the I key; it shows only the fields a photo has. veto: fewer or other fields.
- **Old litebox files keep working:** a file refreshed before this change has no info fields until it is refreshed
  again, and gets the default settings.

## Owed

Nothing owed.

## Later changes

- 2026-11-18: Chris added a logo and a header-text setting. His words, word for word: "here is a logo to
  incorporate into the top header. Please allow the header text to be customized in the settings" (with the logo
  image, kept as `assets/logo.png`), and "can't the logo be embedded in the html page like the thumbnails?" (it is:
  the page carries it as text, and the drive still holds only `litebox.html` and `photos/`).
  - **R9 Logo.** The logo sits at the left of the header bar, before the header text.
  - **R10 Header text.** A "Header text" setting in setup replaces "litebox" in the header bar.
  - Defaulted: **an empty Header text shows "litebox".** veto: an empty field shows the logo alone.
  - Defaulted: **the browser tab shows the header text as its title, and the logo as its icon** (the icon with the
    logo's cut-outs filled dark, so it shows on a light tab bar too). veto: the tab keeps "litebox", or no icon.
  - Defaulted: **on phones the logo and header text take the top line of the bar**, so a long header text never
    squeezes the album name and count; on wider screens they share one line, and a very long text ends in "…"
    with the full text on hover. veto: one line on phones too.
- 2026-11-18: Chris reported, word for word: "the header text isn't being displayed in the page and I would like to
  append '| litebox' to the end of the page title".
  - **R11 Tab title.** With a header text set, the browser tab reads "<header text> | litebox"; with none, "litebox".
    The header bar itself shows the header text alone.
  - The missing header text did not reproduce here (Chromium 156 and Firefox 159, 360 to 1280 px wide, album grid
    and inside an album). The bar no longer lets anything squeeze the header text narrower than the text itself,
    and a test checks it is drawn at full width. Which browser Chris saw it in is owed.
- 2026-11-18: Chris reported, word for word: "when I use the setup form to enter the header text it doesn't appear to
  save the same way the footer text does. I click save, download the new file, replace it, but the header continues
  to display the placeholder text (litebox). When I enter setup again the header text is not there anymore".
  - Checked: the file setup builds carries the header text beside the footer, in Chromium 156 and Firefox 159. The
    likely cause is the download's name: with a `litebox.html` already in the downloads folder, browsers save the
    new one as "litebox (1).html" (Safari: "litebox 2.html"), and copying "litebox.html" puts an older save back.
    Not confirmed with Chris yet.
  - Defaulted: **every saved file carries when it was saved, and setup shows it** ("This file was saved …"), so an
    old copy is easy to spot; the download message warns about the renaming. veto: drop the saved line.
- 2026-11-18: Chris reported, word for word: "Same thing. header doesn't get saved, but the footer does. I'm using
  153.6.0esr on macos".
  - **Withdrawn: the download-name explanation above,** and the "did not reproduce" note before it. The real cause
    was in litebox itself, on every browser: the Header text box and the setup panel's heading shared one id
    (`s-title`), so litebox read the heading instead of the box, and the text typed there was never shown or
    saved. The tests used the same id, so they typed into the heading and passed. Fixed by renaming the box
    `s-header`; new checks fail on any repeated id and on a setup field that is not a real input.
  - The saved-time line in setup and the download warning stay: both still hold true. veto as above.
- 2026-11-18: Chris asked, word for word: "When setting up a litebox for the first time it says clicking "refresh"
  does the whole upload bit and then asks you if you want to download the new file. This occurs even though you
  might still want to edit the other setup bits. I think we should update the button to say load/update photoes
  (depends on whether there have already been photos loaded before), remove the download prompt after the refresh
  occurs, but put a green check and timestamp next to the load/update button, and then only download when you
  click download button. there could be a warning on modal dismissal if you haven't downloaded the new file yet."
  - **R12 Load or Update.** The button reads "Load photos" while there are none, "Update photos" after. It only
    reads the photos: no save or download prompt follows.
  - **R13 Check and time.** A green check and the time the photos were loaded show beside that button.
  - **R14 Save on the button only.** litebox.html is saved or downloaded only by the save button in setup.
  - **R15 Warn on close.** Closing setup with photos or settings not yet saved or downloaded asks first.
  - Defaulted: **the save button says "Download litebox.html" on Firefox and Safari, and "Save litebox.html" on
    Chrome and Edge**, which write the file in place on the drive. veto: "Download" everywhere.
  - Defaulted: **after saving, a green check and the time show beside the save button too**, and after a download
    the copy-onto-the-drive instructions show below it. Any later change hides the check again. veto: no check there.
  - Defaulted: **closing the browser tab with anything unsaved also warns** (the browser's own "leave page?" box), so
    minutes of loading are not lost by accident. veto: warn on closing setup only.
  - Defaulted: **the skipped-files list moved into setup**, under the Photos section, since the pop-up it lived in is
    gone. veto: none needed.
  - Defaulted: **"This copy of litebox.html was saved …" shows only when the open copy has a save time.** veto: also
    say "not saved yet" on a new copy.
- 2026-11-18: Chris asked, word for word: "let's make the footer sticky".
  - **R16 Sticky footer.** The footer line stays at the bottom of the window while the photos scroll, with the
    header bar's see-through dark background. It still shows only when a footer line is set.
- 2026-11-18, from `looseends`: Chris answered the open offers: a sort setting "Yes, add the setting"; the save
  button labels "Keep it"; the saved-time line and rename warning "Keep both".
  - **R17 Order.** Setup offers "Newest first" (the default) or "By folder and file name" (numbers in numeric
    order), saved with the other settings; albums, All photos and search results follow it.
  - Defaulted: **an album's cover is the first photo in the chosen order**, so with "By folder and file name" it is
    the first by name, no longer the newest. veto: always the newest.
