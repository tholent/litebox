// Run 2: open the rebuilt litebox and check the grid, viewer, keys and slideshow.
// photos/c.png has been moved off the test drive, to check the "not on the drive any more" message.
(async function () {
  'use strict';
  const R = [];
  const ok = (name, cond, info) => R.push({ name, ok: !!cond, info: cond ? null : (info === undefined ? null : info) });
  const lb = window.litebox;
  const $ = (id) => document.getElementById(id);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const text = (id) => $(id).textContent;
  async function settled() {           // wait for the viewer's photo to load or fail
    for (let i = 0; i < 100; i++) {
      const img = $('v-img');
      if (!$('v-missing').hidden || (img.complete && img.naturalWidth > 0)) return;
      await sleep(50);
    }
  }
  const key = (k) => document.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true }));

  try {
    const grid = $('grid');
    ok('grid shows six tiles', grid.children.length === 6, grid.children.length);
    ok('"No photos yet" is hidden', $('empty').hidden);
    ok('header counts the photos', text('meta').startsWith('6 photos · updated '), text('meta'));
    await sleep(200);
    ok('visible tiles get their thumbnails', (grid.children[0].firstChild.src || '').startsWith('data:image/jpeg'));
    ok('tiles are labelled with the description or file name',
      grid.children[0].getAttribute('aria-label') === 'h #1 & more.jpg' &&
      grid.children[1].getAttribute('aria-label') === 'Café on the corner – ünïcode',
      [grid.children[0].getAttribute('aria-label'), grid.children[1].getAttribute('aria-label')]);

    grid.children[0].click();
    ok('clicking a tile opens the viewer', !$('viewer').hidden && lb.index === 0);
    await settled();
    ok('full-size photo loads from a name with # and &', $('v-img').naturalWidth === 900, $('v-img').naturalWidth);
    ok('caption: file name', text('v-file') === 'h #1 & more.jpg', text('v-file'));
    ok('caption: date taken', /2024/.test(text('v-when')) && !/file date/.test(text('v-when')), text('v-when'));
    ok('counter', text('v-count') === '1 / 6', text('v-count'));

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
    ok('caption: description of a.jpg', text('v-desc') === 'Lake at dawn', text('v-desc'));

    key('ArrowLeft');
    ok('left arrow steps back', lb.index === 2);
    lb.open(5);
    ok('camera placeholder shows no description', text('v-desc') === '', text('v-desc'));
    lb.next();
    ok('stepping past the last photo wraps to the first', lb.index === 0);
    key('Escape');
    ok('Esc closes the viewer', $('viewer').hidden);
    ok('focus returns to the photo grid', document.activeElement && document.activeElement.classList.contains('tile'));

    lb.slideMs = 120;
    $('play-all').click();
    ok('Slideshow opens the viewer at the newest photo', !$('viewer').hidden && lb.index === 0 && lb.playing);
    await sleep(400);
    ok('slideshow advances on its own', lb.index >= 2, lb.index);
    key(' ');
    const paused = lb.index;
    ok('Space pauses the slideshow', !lb.playing);
    await sleep(300);
    ok('paused slideshow stays put', lb.index === paused, [paused, lb.index]);
    key(' ');
    ok('Space starts it again', lb.playing);
    key('Escape');
    ok('Esc stops the slideshow', !lb.playing && $('viewer').hidden);

    $('refresh').click();
    ok('Refresh opens the refresh panel', !$('panel').hidden && /Choose the folder/.test($('p-body').textContent));
    key('Escape');
    ok('Esc closes the refresh panel', $('panel').hidden);
  } catch (err) {
    ok('harness 2 ran without errors', false, String((err && err.stack) || err));
  }
  const pre = document.createElement('pre');
  pre.id = 'lb-results';
  pre.textContent = JSON.stringify(R);
  document.body.appendChild(pre);
})();
