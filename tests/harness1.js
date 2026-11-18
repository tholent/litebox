// Run 1: refresh an empty litebox from the test drive's files and check the photo list it builds.
// Injected after litebox's own script by tests/run.py; reports into <pre id="lb-results">.
(async function () {
  'use strict';
  const R = [];
  const ok = (name, cond, info) => R.push({ name, ok: !!cond, info: cond ? null : (info === undefined ? null : info) });
  const lb = window.litebox;

  function load(f) {
    return new Promise((resolve, reject) => {
      const x = new XMLHttpRequest();
      x.open('GET', f.rel.split('/').map(encodeURIComponent).join('/'));
      x.responseType = 'blob';
      x.onload = () => resolve(new File([x.response], f.rel.split('/').pop(), { lastModified: f.mtime }));
      x.onerror = () => reject(new Error('could not load ' + f.rel));
      x.send();
    });
  }
  function pixel(dataUrl, x, y) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const c = document.createElement('canvas');
        c.width = img.naturalWidth; c.height = img.naturalHeight;
        const ctx = c.getContext('2d');
        ctx.drawImage(img, 0, 0);
        resolve({ w: img.naturalWidth, h: img.naturalHeight, rgb: Array.from(ctx.getImageData(x, y, 1, 1).data.slice(0, 3)) });
      };
      img.onerror = () => resolve(null);
      img.src = dataUrl;
    });
  }
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  try {
    ok('empty litebox shows the "No photos yet" message', !document.getElementById('empty').hidden);
    ok('empty litebox hides the slideshow button', document.getElementById('play-all').hidden);
    ok('empty litebox offers "Set up litebox"', !document.getElementById('setup-start').hidden &&
      document.getElementById('setup-start').offsetParent !== null);
    ok('no Refresh or Settings button outside setup', !Array.from(document.querySelectorAll('header button, footer button'))
      .some((b) => /refresh|setting/i.test(b.textContent)));

    const files = window.MANIFEST.files;
    const expectEntries = [
      'photos/2021 lake/a.jpg', 'photos/10 scans/scan-001.jpg', 'photos/2 misc/deep/m.jpg', 'photos/IMG_0002.HEIC', 'photos/b-rotated.jpg', 'photos/broken.jpg',
      'photos/c.png', 'photos/clip.mp4', 'photos/d.webp', 'photos/e.jpg', 'photos/h #1 & more.jpg',
    ].sort();

    const picked = lb.entriesFromPicked(files.map((f) => ({ rel: 'drive/' + f.rel, getFile: () => load(f) })));
    const got = picked ? picked.map((e) => e.path).sort() : null;
    ok('picking the drive folder takes only photos/, without hidden files', same(got, expectEntries), got);

    const pickedB = lb.entriesFromPicked(files.filter((f) => f.rel.startsWith('photos/'))
      .map((f) => ({ rel: f.rel, getFile: () => load(f) })));
    const gotB = pickedB ? pickedB.map((e) => e.path).sort() : null;
    ok('picking photos/ itself gives the same list', same(gotB, expectEntries), gotB);
    ok('a folder without photos/ is refused', lb.entriesFromPicked([{ rel: 'stuff/a.jpg', getFile: null }]) === null);

    let lastProgress = null;
    const d = await lb.buildIndex(picked, (done, total) => { lastProgress = [done, total]; });
    ok('progress reaches the end', same(lastProgress, [8 + 1, 8 + 1]), lastProgress);   // 8 photos + broken.jpg

    const order = d.photos.map((p) => p.path);
    ok('eight photos, newest first', same(order, [
      'photos/2 misc/deep/m.jpg', 'photos/h #1 & more.jpg', 'photos/b-rotated.jpg', 'photos/c.png', 'photos/2021 lake/a.jpg',
      'photos/d.webp', 'photos/e.jpg', 'photos/10 scans/scan-001.jpg']), order);
    ok('skipped files are reported with reasons', same(d.skipped, [
      { path: 'photos/broken.jpg', why: 'could not be read' },
      { path: 'photos/clip.mp4', why: 'not a format browsers can show' },
      { path: 'photos/IMG_0002.HEIC', why: 'not a format browsers can show' }]), d.skipped);

    const by = Object.fromEntries(d.photos.map((p) => [p.path.split('/').pop(), p]));
    const a = by['a.jpg'], b = by['b-rotated.jpg'], c = by['c.png'], dw = by['d.webp'], e = by['e.jpg'], h = by['h #1 & more.jpg'];
    ok('JPEG: date taken from EXIF', a && a.taken === '2021-06-01T10:00:00' && a.dateFrom === 'exif', a && a.taken);
    ok('JPEG: EXIF description', a && a.description === 'Lake at dawn', a && a.description);
    ok('UTF-8 description kept intact', b && b.description === 'Café on the corner – ünïcode', b && b.description);
    ok('rotated photo measured the right way up', b && b.width === 400 && b.height === 800, b && [b.width, b.height]);
    ok('PNG without EXIF falls back to the file date', c && c.taken === '2022-03-04T12:00:00' && c.dateFrom === 'file',
      c && [c.taken, c.dateFrom]);
    ok('WebP: EXIF date and description', dw && dw.taken === '2020-12-25T09:00:00' && dw.description === 'Christmas morning',
      dw && [dw.taken, dw.description]);
    ok('camera placeholder description hidden', e && e.description === '', e && e.description);
    ok('no description gives an empty one', h && h.description === '', h && h.description);

    const s = by['scan-001.jpg'], m = by['m.jpg'];
    ok('scan: scanner, resolution, software, artist, copyright read',
      s && same(s.info, { camera: 'EPSON Perfection V600', software: 'Epson Scan 2', artist: 'Chris W',
        copyright: '© Family archive', dpi: 600 }), s && s.info);
    ok('scan: no date taken, so the file date is used', s && s.dateFrom === 'file' && s.taken === '2018-01-01T12:00:00',
      s && [s.taken, s.dateFrom]);
    ok('phone photo: camera, lens, exposure, aperture, ISO, focal length read',
      m && m.info.camera === 'Apple iPhone 15' && m.info.lens === 'iPhone 15 back camera' &&
      Math.abs(m.info.exposure - 0.004) < 1e-9 && m.info.aperture === 1.8 && m.info.iso === 64 &&
      Math.abs(m.info.focal - 6.86) < 1e-9, m && m.info);
    ok('file size recorded', d.photos.every((p) => p.bytes > 0));
    ok('a photo with no EXIF has empty details', c && same(c.info, {}), c && c.info);

    const thumbs = await Promise.all(d.photos.map((p) => pixel(p.thumb, 0, 0)));
    ok('every thumbnail is a 240px square JPEG', d.photos.every((p) => p.thumb.startsWith('data:image/jpeg;base64,')) &&
      thumbs.every((t) => t && t.w === 240 && t.h === 240), thumbs.map((t) => t && [t.w, t.h]));
    const top = await pixel(b.thumb, 120, 30), bottom = await pixel(b.thumb, 120, 210);
    ok('rotated photo thumbnail turned the right way (red top, blue bottom)',
      top && bottom && top.rgb[0] > 150 && top.rgb[2] < 100 && bottom.rgb[2] > 150 && bottom.rgb[0] < 100,
      [top && top.rgb, bottom && bottom.rgb]);
    const avg = thumbs.length ? Math.round(d.photos.reduce((s, p) => s + p.thumb.length, 0) / d.photos.length) : 0;
    ok('thumbnails stay small (under 20 KB each)', avg < 20000, avg);

    // A tricky description must not break out of the page's data block.
    const tricky = JSON.parse(JSON.stringify(d));
    tricky.photos[0].description = '</script><b>x</b>' + String.fromCharCode(0x2028);
    tricky.settings = { title: '</script> title', footer: '</script> footer', showDates: false, slideSeconds: 9 };
    const html = lb.makeHtml(d);
    const parsed = new DOMParser().parseFromString(lb.makeHtml(tricky), 'text/html');
    const back = JSON.parse(parsed.getElementById('litebox-data').textContent);
    ok('saved list survives a description containing </script>', back.photos[0].description === tricky.photos[0].description);
    ok('saved settings survive too', same(back.settings, tricky.settings), back.settings);
    const again = JSON.parse(new DOMParser().parseFromString(html, 'text/html').getElementById('litebox-data').textContent);
    ok('saved file holds the new photo list', same(again.photos.map((p) => p.path), order));
    ok('saved file starts with a doctype', html.startsWith('<!doctype html>'));

    // --- setup: Load photos only reads them; litebox.html is saved only by the save button
    const $ = (id) => document.getElementById(id);
    const text = (id) => $(id).textContent;
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    location.hash = '#setup';
    await sleep(60);
    ok('a new litebox offers "Load photos"', text('s-refresh') === 'Load photos', text('s-refresh'));
    ok('no check mark before photos are loaded', $('s-loaded').hidden);
    ok('Chrome and Edge get "Save" (in place)', text('s-save') === 'Save ' + location.pathname.split('/').pop(), text('s-save'));
    await lb.refresh(picked);
    ok('loading photos opens no save or download prompt', $('panel').hidden && !$('setup').hidden);
    ok('a check and the time show by the button', !$('s-loaded').hidden && /^\u2713 Loaded .+/.test(text('s-loaded')),
      text('s-loaded'));
    ok('the button now says "Update photos"', text('s-refresh') === 'Update photos', text('s-refresh'));
    ok('the gallery already shows the loaded photos', lb.data.photos.length === 8 && !$('albums').hidden);
    ok('skipped files are listed in setup', /3 files litebox can.t show/.test(text('s-skipped')), text('s-skipped'));
    ok('setup flags the loaded photos as not saved yet', $('s-dirty').classList.contains('err') &&
      /photos you loaded/.test(text('s-dirty')), text('s-dirty'));
    ok('nothing says saved yet', $('s-done').hidden && $('s-after').hidden);

    const realConfirm = window.confirm;
    let asked = 0;
    window.confirm = () => { asked++; return false; };
    $('s-close').click();
    ok('closing setup before saving warns, and stays open when told to', asked === 1 && !$('setup').hidden);

    // The download route, as on Firefox and Safari. Catch the download instead of saving a file.
    window.showDirectoryPicker = undefined;
    $('s-header').dispatchEvent(new Event('input', { bubbles: true }));
    ok('other browsers get "Download"', /^Download /.test(text('s-save')), text('s-save'));
    let grabbed = null;
    document.addEventListener('click', (e) => {
      if (e.target.download) { e.preventDefault(); grabbed = e.target.href; }
    }, true);
    $('s-save').click();
    await sleep(20);
    ok('the button downloads litebox.html', !!grabbed);
    const got1 = grabbed ? JSON.parse(new DOMParser().parseFromString(await (await fetch(grabbed)).text(), 'text/html')
      .getElementById('litebox-data').textContent) : null;
    ok('the download holds the loaded photos and when it was saved', got1 && got1.photos.length === 8 && !!got1.saved,
      got1 && got1.photos.length);
    ok('after downloading: a check and the time by the button', !$('s-done').hidden &&
      /^\u2713 Downloaded at .+/.test(text('s-done')), text('s-done'));
    ok('after downloading: how to copy it onto the drive', !$('s-after').hidden && /replacing the old one/.test(text('s-after')));
    ok('setup no longer flags anything unsaved', !$('s-dirty').classList.contains('err'));
    $('s-footer').value = 'changed';
    $('s-footer').dispatchEvent(new Event('input', { bubbles: true }));
    ok('a later change hides the check again', $('s-done').hidden && $('s-dirty').classList.contains('err'));
    $('s-footer').value = '';
    $('s-footer').dispatchEvent(new Event('input', { bubbles: true }));
    asked = 0;
    $('s-close').click();
    ok('closing after downloading does not warn', asked === 0 && $('setup').hidden);
    window.confirm = realConfirm;

    const out = document.createElement('pre');
    out.id = 'lb-out';
    out.textContent = btoa(unescape(encodeURIComponent(html)));
    document.body.appendChild(out);
  } catch (err) {
    ok('harness 1 ran without errors', false, String((err && err.stack) || err));
  }
  const pre = document.createElement('pre');
  pre.id = 'lb-results';
  pre.textContent = JSON.stringify(R);
  document.body.appendChild(pre);
})();
