// Run 2: open the rebuilt litebox and check albums, search, the viewer, info panel, keys, slideshow and setup.
// photos/c.png has been moved off the test drive, to check the "not on the drive any more" message.
(async function () {
  'use strict';
  const R = [];
  const ok = (name, cond, info) => R.push({ name, ok: !!cond, info: cond ? null : (info === undefined ? null : info) });
  const lb = window.litebox;
  const $ = (id) => document.getElementById(id);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const text = (id) => $(id).textContent;
  const visible = (id) => !$(id).hidden && $(id).getClientRects().length > 0;
  async function settled() {           // wait for the viewer's photo to load or fail
    for (let i = 0; i < 100; i++) {
      const img = $('v-img');
      if (!$('v-missing').hidden || (img.complete && img.naturalWidth > 0)) return;
      await sleep(50);
    }
  }
  async function nav(hash) { location.hash = hash; await sleep(60); }
  const key = (k) => document.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true }));
  async function type(value) {
    $('search').value = value;
    $('search').dispatchEvent(new Event('input', { bubbles: true }));
    await sleep(10);
  }
  const albumNames = () => Array.from($('albums').children).map((a) => a.querySelector('.name').textContent);
  const infoRows = () => {
    const dts = Array.from($('v-info-list').children).filter((x) => x.tagName === 'DT');
    return Object.fromEntries(dts.map((dt) => [dt.textContent, dt.nextSibling.textContent]));
  };

  try {
    // --- the album grid is the opening view
    ok('opens on the album grid', visible('albums') && $('grid').hidden);
    ok('albums in name order, numbers in order, Unsorted last, after "All photos"',
      JSON.stringify(albumNames()) === JSON.stringify(['All photos', '2 misc', '10 scans', '2021 lake', 'Unsorted']),
      albumNames());
    ok('album counts', Array.from($('albums').children).map((a) => a.querySelector('.n').textContent).join('|') ===
      '8 photos|1 photo|1 photo|1 photo|5 photos');
    ok('header counts albums and photos', text('meta') === '4 albums · 8 photos', text('meta'));
    ok('no Refresh or Settings anywhere on the page', !Array.from(document.querySelectorAll('button'))
      .some((b) => b.offsetParent !== null && /refresh|setting|load photos|update photos|download|save/i.test(b.textContent)));
    ok('footer hidden while the footer line is empty', $('footer').hidden);
    ok('header shows the logo', $('logo').complete && $('logo').naturalWidth === 84 && /^data:image\/png/.test($('logo').src));
    ok('header text and tab title default to litebox', text('brand-text') === 'litebox' && document.title === 'litebox',
      [text('brand-text'), document.title]);
    ok('the page carries its own tab icon', /^data:image\/png/.test(document.querySelector('link[rel=icon]').href));

    // --- open an album
    $('albums').children[4].click();
    await sleep(60);
    ok('clicking an album shows its photos', visible('grid') && $('grid').children.length === 5 && lb.album === '',
      [$('grid').children.length, lb.album]);
    ok('address names the album, so Back works', location.hash === '#album=', location.hash);
    ok('album title and count', text('title') === 'Unsorted' && text('meta') === '5 photos', [text('title'), text('meta')]);
    ok('back to albums link shows', visible('back'));
    const grid = $('grid');
    for (let t = 0; t < 30 && !(grid.children[0].firstChild.src || '').startsWith('data:'); t++) await sleep(100);
    ok('visible tiles get their thumbnails', (grid.children[0].firstChild.src || '').startsWith('data:image/jpeg'));
    ok('tiles are labelled with the description or file name',
      grid.children[0].getAttribute('aria-label') === 'h #1 & more.jpg' &&
      grid.children[1].getAttribute('aria-label') === 'Café on the corner – ünïcode',
      [grid.children[0].getAttribute('aria-label'), grid.children[1].getAttribute('aria-label')]);

    // --- the viewer inside an album
    grid.children[0].click();
    ok('clicking a tile opens the viewer', !$('viewer').hidden && lb.index === 0);
    await settled();
    ok('full-size photo loads from a name with # and &', $('v-img').naturalWidth === 900, $('v-img').naturalWidth);
    ok('caption: file name', text('v-file') === 'h #1 & more.jpg', text('v-file'));
    ok('caption: date taken', /2024/.test(text('v-when')) && !/file date/.test(text('v-when')), text('v-when'));
    ok('counter counts within the album', text('v-count') === '1 / 5', text('v-count'));
    key('ArrowRight');
    await settled();
    ok('right arrow steps forward', lb.index === 1);
    ok('caption: EXIF description', text('v-desc') === 'Café on the corner – ünïcode', text('v-desc'));
    ok('rotated photo shows the right way up', $('v-img').naturalWidth === 400 && $('v-img').naturalHeight === 800,
      [$('v-img').naturalWidth, $('v-img').naturalHeight]);
    lb.next();
    await settled();
    ok('a photo missing from the drive says so', !$('v-missing').hidden && $('v-img').hidden);
    ok('file-date fallback is labelled', /file date/.test(text('v-when')), text('v-when'));
    lb.next();
    await settled();
    ok('the missing message clears on the next photo', $('v-missing').hidden && !$('v-img').hidden);
    ok('caption: description of d.webp', text('v-desc') === 'Christmas morning', text('v-desc'));
    key('ArrowLeft');
    ok('left arrow steps back', lb.index === 2);
    lb.open(4);
    ok('camera placeholder shows no description', text('v-desc') === '', text('v-desc'));
    lb.next();
    ok('stepping past the last photo wraps to the first of the album', lb.index === 0);
    key('Escape');
    ok('Esc closes the viewer', $('viewer').hidden);
    ok('focus returns to the photo grid', document.activeElement && document.activeElement.classList.contains('tile'));

    // --- info panel
    await nav('album=10%20scans');
    ok('albums open from the address', lb.album === '10 scans' && $('grid').children.length === 1, lb.album);
    lb.open(0);
    ok('details panel starts closed', $('v-info').hidden);
    key('i');
    ok('I opens the details panel', !$('v-info').hidden && $('v-info-btn').getAttribute('aria-pressed') === 'true');
    const rows = infoRows();
    ok('details: scanner, resolution, software, artist, copyright',
      rows.Camera === 'EPSON Perfection V600' && rows.Resolution === '600 dpi' && rows.Software === 'Epson Scan 2' &&
      rows.Artist === 'Chris W' && rows.Copyright === '© Family archive', rows);
    ok('details: file, album, size, file size', rows.File === 'scan-001.jpg' && rows.Album === '10 scans' &&
      rows.Size === '700 × 500 pixels' && /KB$/.test(rows['File size']), rows);
    ok('details: a scan shows its file date', /2018/.test(rows['File date'] || ''), rows);
    ok('details: no camera fields a scan lacks', !('Exposure' in rows) && !('Lens' in rows), rows);
    $('v-info-btn').click();
    ok('the ⓘ button closes it again', $('v-info').hidden);
    $('v-info-btn').click();
    key('Escape');

    await nav('album=2%20misc');
    ok('a folder two deep belongs to its top-level album', $('grid').children.length === 1 && lb.list[0].path === 'photos/2 misc/deep/m.jpg');
    lb.open(0);
    ok('details panel remembered as open', !$('v-info').hidden);
    const r2 = infoRows();
    ok('details: phone camera fields', r2.Camera === 'Apple iPhone 15' && r2.Lens === 'iPhone 15 back camera' &&
      r2.Exposure === '1/250 s' && r2.Aperture === 'f/1.8' && r2.ISO === '64' && r2['Focal length'] === '6.9 mm', r2);
    key('i');
    key('Escape');

    // --- search
    $('back').click();
    await sleep(60);
    ok('"‹ Albums" goes back to the album grid', visible('albums') && lb.album === null);
    ok('search box shows, searching everything from the album grid', visible('search') && $('search').placeholder === 'Search all photos');
    await type('christmas');
    ok('search by description', $('grid').children.length === 1 && lb.list[0].path === 'photos/d.webp' &&
      text('meta') === '1 match', [lb.list.map((p) => p.path), text('meta')]);
    await type('cafe corner');
    ok('search ignores accents and needs every word', lb.list.length === 1 && lb.list[0].path === 'photos/b-rotated.jpg',
      lb.list.map((p) => p.path));
    await type('lake');
    ok('search matches album names', lb.list.length === 1 && lb.list[0].path === 'photos/2021 lake/a.jpg', lb.list.map((p) => p.path));
    await type('scan-001');
    ok('search matches file names', lb.list.length === 1, lb.list.map((p) => p.path));
    await type('zebra');
    ok('no match says so', visible('nothing') && /zebra/.test(text('nothing')) && $('grid').hidden);
    await type('');
    ok('clearing search brings the albums back', visible('albums'));
    await nav('album=');
    await type('christmas');
    ok('inside an album, search covers that album', $('search').placeholder === 'Search this album' && lb.list.length === 1);
    await type('lake');
    ok('…and only that album', lb.list.length === 0);
    await type('');

    // --- slideshow and its speed slider
    lb.slideMs = 120;
    $('play-all').click();
    ok('Slideshow plays the album from its newest photo', !$('viewer').hidden && lb.index === 0 && lb.playing);
    ok('speed slider shows while the slideshow runs', visible('v-speed'));
    await sleep(400);
    ok('slideshow advances on its own', lb.index >= 2, lb.index);
    $('v-speed-range').value = 7;
    $('v-speed-range').dispatchEvent(new Event('input', { bubbles: true }));
    ok('slider sets the seconds per photo', lb.slideMs === 7000 && text('v-speed-out') === '7 s', [lb.slideMs, text('v-speed-out')]);
    key(' ');
    ok('Space pauses the slideshow and hides the slider', !lb.playing && $('v-speed').hidden);
    key(' ');
    ok('Space starts it again', lb.playing);
    key('Escape');
    ok('Esc stops the slideshow', !lb.playing && $('viewer').hidden);

    // --- hidden setup
    await nav('setup');
    ok('#setup opens the setup panel', visible('setup'));
    ok('setup offers "Update photos" once photos are in', visible('s-refresh') && text('s-refresh') === 'Update photos',
      text('s-refresh'));
    ok('setup shows a check and when the photos were loaded', visible('s-loaded') && /^\u2713 Loaded .+/.test(text('s-loaded')),
      text('s-loaded'));
    ok('setup lists the files litebox skipped', /3 files litebox can.t show/.test(text('s-skipped')), text('s-skipped'));
    ok('setup reports photos and albums', /8 photos in 4 albums/.test(text('s-photos')), text('s-photos'));
    const ids = Array.from(document.querySelectorAll('[id]')).map((e) => e.id);
    ok('every id on the page is used once', ids.length === new Set(ids).size,
      ids.filter((id, i) => ids.indexOf(id) !== i));
    ok('every setup field is a real input', ['s-header', 's-footer', 's-dates', 's-seconds']
      .every((id) => $(id).tagName === 'INPUT' && $(id).closest('#setup')));
    ok('setup shows the default settings', $('s-header').value === '' && $('s-footer').value === '' && $('s-dates').checked && $('s-seconds').value === '5');
    $('s-header').value = 'Our family photos';
    $('s-header').dispatchEvent(new Event('input', { bubbles: true }));
    ok('header text and tab title change straight away', text('brand-text') === 'Our family photos' &&
      document.title === 'Our family photos | litebox', [text('brand-text'), document.title]);
    ok('header text is drawn at full width', $('brand-text').scrollWidth > 60 &&
      $('brand-text').clientWidth === $('brand-text').scrollWidth, [$('brand-text').clientWidth, $('brand-text').scrollWidth]);
    $('s-header').value = '  ';
    $('s-header').dispatchEvent(new Event('input', { bubbles: true }));
    ok('blank header text falls back to litebox', text('brand-text') === 'litebox' && document.title === 'litebox' &&
      lb.data.settings.title === '');
    $('s-header').value = 'Our family photos';
    $('s-header').dispatchEvent(new Event('input', { bubbles: true }));
    $('s-footer').value = 'For Mum, with love';
    $('s-footer').dispatchEvent(new Event('input', { bubbles: true }));
    ok('footer line shows straight away', !$('footer').hidden && text('footer') === 'For Mum, with love');
    $('s-dates').checked = false;
    $('s-dates').dispatchEvent(new Event('change', { bubbles: true }));
    $('s-seconds').value = '8';
    $('s-seconds').dispatchEvent(new Event('input', { bubbles: true }));
    ok('unsaved changes are flagged', $('s-dirty').classList.contains('err'));
    ok('settings land in the data that gets saved', JSON.stringify(lb.data.settings) ===
      JSON.stringify({ title: 'Our family photos', footer: 'For Mum, with love', showDates: false, slideSeconds: 8 }),
      lb.data.settings);
    const savedBack = JSON.parse(new DOMParser().parseFromString(lb.makeHtml(lb.data), 'text/html')
      .getElementById('litebox-data').textContent);
    ok('a saved file carries the settings', savedBack.settings.title === 'Our family photos' &&
      savedBack.settings.footer === 'For Mum, with love' && savedBack.settings.showDates === false);
    ok('no saved-time line for a copy never saved from setup', $('s-saved').hidden);
    const stampedSave = lb.stamped();
    const stampedBack = JSON.parse(new DOMParser().parseFromString(stampedSave.html, 'text/html')
      .getElementById('litebox-data').textContent);
    ok('the file setup saves carries the header text and when it was saved',
      stampedBack.settings.title === 'Our family photos' && stampedBack.saved === stampedSave.at, stampedBack.settings);
    const realConfirm = window.confirm;
    let asked = false;
    window.confirm = () => { asked = true; return true; };
    $('s-close').click();
    window.confirm = realConfirm;
    ok('closing with unsaved changes asks first', asked);
    ok('closing setup leaves the address without #setup', $('setup').hidden && location.hash !== '#setup', location.hash);
    ok('slideshow default follows the setting', lb.slideMs === 8000, lb.slideMs);
    lb.open(0);
    await settled();
    ok('dates hidden from captions', text('v-when') === '', text('v-when'));
    key('i');
    ok('dates hidden from details', !('Taken' in infoRows()) && !('File date' in infoRows()), infoRows());
    key('i');
    key('Escape');

    // --- reopening a saved file: its header text shows, and setup says when it was saved
    lb.load(stampedBack);
    ok('a reopened file shows its header text', text('brand-text') === 'Our family photos');
    await nav('setup');
    ok('setup shows when the file was saved', /^This copy of .+ was saved .+\.$/.test(text('s-saved')), text('s-saved'));
    ok('setup shows the saved header text', $('s-header').value === 'Our family photos', $('s-header').value);
    window.confirm = () => true;
    $('s-close').click();
    window.confirm = realConfirm;

    // --- a drive with no subfolders skips the album grid
    const flat = JSON.parse(JSON.stringify(lb.data));
    flat.photos = flat.photos.filter((p) => p.path.split('/').length === 2);
    lb.load(flat);
    await nav('');
    ok('no subfolders: photos show straight away', visible('grid') && $('albums').hidden && $('grid').children.length === 5);
    ok('no subfolders: no back link or album title', $('back').hidden && text('title') === '');
  } catch (err) {
    ok('harness 2 ran without errors', false, String((err && err.stack) || err));
  }
  const pre = document.createElement('pre');
  pre.id = 'lb-results';
  pre.textContent = JSON.stringify(R);
  document.body.appendChild(pre);
})();
