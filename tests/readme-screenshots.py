#!/usr/bin/env python3
# Copyright 2026 Chris Wells
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Make the README screenshots from a real litebox drive.

Usage: python3 tests/readme-screenshots.py [drive]

The drive (default samples/drive) holds a photos/ folder, as a real litebox drive does. The script:
1. loads those photos into a fresh litebox.html with litebox's own Load photos code (buildIndex), in headless
   Chrome, with the settings below, and writes it to <drive>/litebox.html;
2. opens that file and saves screenshots to docs/images/ as JPEG.
The photos are only read. Needs: python3 with Pillow, and Chromium or Chrome.
"""
import base64
import html
import io
import json
import re
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402  (the test runner: its real-clock Chrome helpers)

ROOT = Path(__file__).resolve().parent.parent
DRIVE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "samples" / "drive"
IMAGES = ROOT / "docs" / "images"
SETTINGS = {"title": "Our photos", "footer": "Sample photos from Pexels", "showDates": False,
            "slideSeconds": 5, "order": "newest"}

BUILD = """
(async function () {
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
  const out = document.createElement('pre');
  try {
    const picked = window.MANIFEST.files.map((f) => ({ rel: 'drive/' + f.rel, getFile: () => load(f) }));
    const entries = lb.entriesFromPicked(picked);
    const d = await lb.buildIndex(entries, () => {});
    d.settings = window.SETTINGS;
    out.id = 'lb-out';
    out.textContent = btoa(unescape(encodeURIComponent(lb.makeHtml(d))));
  } catch (e) { out.id = 'lb-error'; out.textContent = String(e && e.stack || e); }
  document.body.appendChild(out);
  const done = document.createElement('pre');
  done.id = 'lb-results';
  done.textContent = '[]';
  document.body.appendChild(done);
})();
"""

# Visible images have loaded (or the details panel is the thing being waited on).
LOADED = """(() => Array.from(document.images).filter((i) => {
  const r = i.getBoundingClientRect();
  return i.getClientRects().length && r.bottom > 0 && r.top < innerHeight && i.src;
}).every((i) => i.complete && i.naturalWidth > 0))()"""


def build():
    files = [{"rel": p.relative_to(DRIVE).as_posix(), "mtime": int(p.stat().st_mtime * 1000)}
             for p in sorted((DRIVE / "photos").rglob("*")) if p.is_file()]
    if not files:
        sys.exit(f"no photos in {DRIVE / 'photos'}")
    work = DRIVE / ".build"
    work.mkdir(exist_ok=True)
    (work / "manifest.js").write_text("window.MANIFEST = " + json.dumps({"files": files}) + ";\n"
                                      "window.SETTINGS = " + json.dumps(SETTINGS) + ";\n")
    (work / "build.js").write_text(BUILD)
    page = DRIVE / "build-litebox.html"
    src = (ROOT / "litebox.html").read_text(encoding="utf-8")
    head, sep, tail = src.rpartition("</body>")
    page.write_text(head + '<script src=".build/manifest.js"></script><script src=".build/build.js"></script>'
                    + sep + tail, encoding="utf-8")
    try:
        results, dom = run.run_page(page, timeout=900)
    finally:
        page.unlink()
    m = re.search(r'<pre id="lb-out">(.*?)</pre>', dom, re.DOTALL)
    if not m:
        err = re.search(r'<pre id="lb-error">(.*?)</pre>', dom, re.DOTALL)
        sys.exit("building litebox.html failed: " + (html.unescape(err.group(1)) if err else str(results)))
    (DRIVE / "litebox.html").write_bytes(base64.b64decode(m.group(1)))
    print(f"wrote {DRIVE / 'litebox.html'} with {len(files)} files")


def shot(name, hash_="", actions="", phone=False, width=1600):
    chrome = run.DevTools((DRIVE / "litebox.html").as_uri() + hash_)
    try:
        target = next(t for t in chrome.call("Target.getTargets")["targetInfos"] if t["type"] == "page")
        chrome.session = chrome.call("Target.attachToTarget", {"targetId": target["targetId"], "flatten": True})[
            "sessionId"]
        if phone:
            chrome.call("Emulation.setDeviceMetricsOverride",
                        {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True})
        else:
            chrome.call("Emulation.setDeviceMetricsOverride",
                        {"width": 1280, "height": 800, "deviceScaleFactor": 2, "mobile": False})
        chrome.call("Page.reload")
        time.sleep(1)
        if actions:
            chrome.evaluate(actions)
            time.sleep(0.5)
        end = time.monotonic() + 60
        while not chrome.evaluate(LOADED) and time.monotonic() < end:
            time.sleep(0.25)
        time.sleep(0.6)  # let fades finish
        png = base64.b64decode(chrome.call("Page.captureScreenshot", {"format": "png"})["data"])
    finally:
        chrome.close()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    w = width if not phone else 780
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = IMAGES / f"{name}.jpg"
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"wrote {out.relative_to(ROOT)} ({im.width}x{im.height}, {out.stat().st_size // 1024} KB)")


def main():
    if not run.CHROMIUM:
        sys.exit("chromium not found")
    build()
    shot("albums")
    shot("viewer", "#album=family", "litebox.open(0); document.getElementById('v-info-btn').click()")
    shot("setup", "#setup")
    shot("phone", phone=True)


if __name__ == "__main__":
    main()
