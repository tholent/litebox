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
"""Test litebox.html end to end in headless Chromium.

Usage: python3 tests/run.py [--screenshots] [--keep]

Each test page runs in headless Chrome on a real clock: run.py asks the page over Chrome's debugging pipe whether
its harness has finished, so a slow machine only takes longer.

1. Builds a test drive in tests/out/drive: a copy of litebox.html, a photos/ folder of made-up photos
   (EXIF dates and descriptions, a rotated photo, PNG, WebP, a broken file, formats browsers can't show,
   hidden system files) and files outside photos/ that must be ignored.
2. Run 1 (tests/harness1.js) refreshes the empty litebox from those files and checks the photo list.
3. Run 2 (tests/harness2.js) opens the rebuilt litebox and checks albums, search, the viewer, info panel,
   keys, slideshow and the hidden setup,
   with one photo removed from the drive to check the "not on the drive any more" message.
4. Checks the photos were not changed, and that litebox.html loads nothing from the internet.

Prints any failures, then one line: "litebox-tests: pass=N fail=M". Exit 0 only when fail=0.
--screenshots also writes PNGs of the gallery and viewer (Chromium and Firefox) to tests/out/.
Needs: python3 with Pillow, and chromium (firefox only for --screenshots).
"""
from __future__ import annotations

import base64
import contextlib
import fcntl
import hashlib
import html
import json
import os
import re
import select
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from PIL.TiffImagePlugin import IFDRational

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
OUT = TESTS / "out"
DRIVE = OUT / "drive"
PHOTOS = DRIVE / "photos"
CHROMIUM = (shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable"))
# Extra Chrome flags, e.g. LITEBOX_CHROME_ARGS="--no-sandbox" on a CI machine.
CHROME_EXTRA = os.environ.get("LITEBOX_CHROME_ARGS", "").split()


def exif_bytes(taken=None, description=None, orientation=None, ifd0=None, exif=None):
    ex = Image.Exif()
    for tag, value in (ifd0 or {}).items():
        ex[tag] = value.encode("utf-8") if isinstance(value, str) else value
    for tag, value in (exif or {}).items():
        ex.get_ifd(0x8769)[tag] = value.encode("utf-8") if isinstance(value, str) else value
    if description is not None:
        ex[0x010E] = description.encode("utf-8")
    if orientation:
        ex[0x0112] = orientation
    if taken:
        ex.get_ifd(0x8769)[0x9003] = taken
    return ex.tobytes()


def picture(w, h, colours):
    """A simple made-up photo: horizontal bands of colour with a circle, so screenshots look like something."""
    im = Image.new("RGB", (w, h), colours[0])
    d = ImageDraw.Draw(im)
    band = w // len(colours)
    for i, c in enumerate(colours):
        d.rectangle([i * band, 0, (i + 1) * band if i < len(colours) - 1 else w, h], fill=c)
    r = min(w, h) // 6
    d.ellipse([w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r], fill=(245, 236, 210))
    return im


def build_drive():
    if OUT.exists():
        shutil.rmtree(OUT)
    (PHOTOS / "2021 lake").mkdir(parents=True)
    (PHOTOS / "10 scans").mkdir()
    (PHOTOS / "2 misc" / "deep").mkdir(parents=True)
    (PHOTOS / ".hidden").mkdir()
    shutil.copy(ROOT / "litebox.html", DRIVE / "litebox.html")

    picture(1200, 800, [(40, 70, 110), (90, 130, 170), (200, 150, 90)]).save(
        PHOTOS / "2021 lake" / "a.jpg", exif=exif_bytes("2021:06:01 10:00:00", "Lake at dawn"))
    # Stored 800x400, left half red and right half blue; orientation 6 shows it 400x800, red on top.
    b = Image.new("RGB", (800, 400), (220, 30, 30))
    ImageDraw.Draw(b).rectangle([400, 0, 800, 400], fill=(30, 60, 220))
    b.save(PHOTOS / "b-rotated.jpg",
           exif=exif_bytes("2023:01:02 08:30:00", "Café on the corner – ünïcode", orientation=6))
    picture(600, 600, [(60, 120, 80), (140, 180, 90)]).save(PHOTOS / "c.png")
    picture(640, 480, [(150, 40, 60), (230, 200, 200)]).save(
        PHOTOS / "d.webp", exif=exif_bytes("2020:12:25 09:00:00", "Christmas morning"))
    picture(500, 700, [(90, 90, 100), (160, 160, 170)]).save(
        PHOTOS / "e.jpg", exif=exif_bytes("2019:05:05 05:05:05", "OLYMPUS DIGITAL CAMERA"))
    picture(900, 600, [(30, 30, 30), (240, 180, 60), (30, 30, 30)]).save(
        PHOTOS / "h #1 & more.jpg", exif=exif_bytes("2024:07:07 07:07:07"))
    # A scan: scanner details, 600 dpi, no date taken.
    picture(700, 500, [(120, 100, 70), (200, 180, 140)]).save(
        PHOTOS / "10 scans" / "scan-001.jpg", dpi=(600, 600),
        exif=exif_bytes(ifd0={0x010F: "EPSON", 0x0110: "Perfection V600", 0x0131: "Epson Scan 2",
                              0x011A: IFDRational(600, 1), 0x011B: IFDRational(600, 1), 0x0128: 2,
                              0x013B: "Chris W", 0x8298: "© Family archive"}))
    # A phone photo two folders deep: it belongs to the album "2 misc".
    picture(800, 600, [(20, 90, 120), (230, 120, 60)]).save(
        PHOTOS / "2 misc" / "deep" / "m.jpg",
        exif=exif_bytes("2025:02:02 12:00:00", ifd0={0x010F: "Apple", 0x0110: "iPhone 15"},
                        exif={0x829A: IFDRational(1, 250), 0x829D: IFDRational(9, 5), 0x8827: 64,
                              0x920A: IFDRational(686, 100), 0xA434: "iPhone 15 back camera"}))
    (PHOTOS / "broken.jpg").write_bytes(b"\xff\xd8\xff\xe0 not really a photo")
    (PHOTOS / "clip.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42")
    (PHOTOS / "IMG_0002.HEIC").write_bytes(b"\x00\x00\x00\x18ftypheic")
    (PHOTOS / "._a.jpg").write_bytes(b"\x00\x05\x16\x07 AppleDouble")
    (PHOTOS / ".DS_Store").write_bytes(b"\x00\x00\x00\x01Bud1")
    picture(100, 100, [(255, 0, 255)]).save(PHOTOS / ".hidden" / "x.jpg")
    picture(100, 100, [(255, 0, 255)]).save(DRIVE / "stray.jpg")
    (DRIVE / "notes.txt").write_text("not a photo\n")

    c_time = time.mktime(datetime(2022, 3, 4, 12, 0, 0).timetuple())
    os.utime(PHOTOS / "c.png", (c_time, c_time))
    s_time = time.mktime(datetime(2018, 1, 1, 12, 0, 0).timetuple())
    os.utime(PHOTOS / "10 scans" / "scan-001.jpg", (s_time, s_time))

    files = []
    for p in sorted(DRIVE.rglob("*")):
        if p.is_file():
            files.append({"rel": p.relative_to(DRIVE).as_posix(), "mtime": int(p.stat().st_mtime * 1000)})
    (OUT / "manifest.js").write_text("window.MANIFEST = " + json.dumps({"files": files}) + ";\n")


def photo_hashes():
    return {p.relative_to(PHOTOS).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(PHOTOS.rglob("*")) if p.is_file()}


def inject(page_html: str, harness: str) -> str:
    tag = f'<script src="../manifest.js"></script><script src="../../{harness}"></script>'
    head, sep, tail = page_html.rpartition("</body>")
    return head + tag + sep + tail


def chromium(args):
    cmd = [CHROMIUM, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--allow-file-access-from-files", "--hide-scrollbars"] + CHROME_EXTRA + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)


class DevTools:
    """Talks to headless Chrome over --remote-debugging-pipe (JSON messages ending in NUL, on fds 3 and 4)."""

    def __init__(self, url):
        to_chrome_r, self.to_chrome = os.pipe()
        self.from_chrome, from_chrome_w = os.pipe()
        # Move Chrome's ends up and out of the way, so placing them on fds 3 and 4 cannot clobber each other.
        hi_r, hi_w = fcntl.fcntl(to_chrome_r, fcntl.F_DUPFD, 20), fcntl.fcntl(from_chrome_w, fcntl.F_DUPFD, 20)
        os.close(to_chrome_r)
        os.close(from_chrome_w)

        def place():
            os.dup2(hi_r, 3)
            os.dup2(hi_w, 4)

        cmd = [CHROMIUM, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               "--allow-file-access-from-files", "--hide-scrollbars", "--window-size=1280,800",
               "--remote-debugging-pipe"] + CHROME_EXTRA + [url]
        # preexec_fn is the only way to put the pipe on the fixed fds 3 and 4 Chrome reads; no threads run here.
        self.proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,  # noqa: PLW1509
                                     stderr=subprocess.PIPE, preexec_fn=place, pass_fds=(3, 4, hi_r, hi_w))
        os.close(hi_r)
        os.close(hi_w)
        self.buf, self.next_id, self.session = b"", 0, None

    def call(self, method, params=None, timeout=30):
        self.next_id += 1
        msg = {"id": self.next_id, "method": method, "params": params or {}}
        if self.session:
            msg["sessionId"] = self.session
        os.write(self.to_chrome, json.dumps(msg).encode() + b"\0")
        end = time.monotonic() + timeout
        while True:
            while b"\0" in self.buf:
                raw, self.buf = self.buf.split(b"\0", 1)
                reply = json.loads(raw)
                if reply.get("id") == self.next_id:
                    if "error" in reply:
                        raise RuntimeError(f"{method}: {reply['error']}")
                    return reply.get("result", {})
            left = end - time.monotonic()
            if left <= 0 or not select.select([self.from_chrome], [], [], left)[0]:
                raise TimeoutError(method)
            chunk = os.read(self.from_chrome, 1 << 16)
            if not chunk:
                raise RuntimeError("chrome closed the connection")
            self.buf += chunk

    def evaluate(self, expression):
        r = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True})
        return r.get("result", {}).get("value")

    def close(self):
        self.session = None
        with contextlib.suppress(OSError, RuntimeError, TimeoutError):
            self.call("Browser.close", timeout=5)
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        for fd in (self.to_chrome, self.from_chrome):
            os.close(fd)
        return self.proc.stderr.read().decode(errors="replace") if self.proc.stderr else ""


def run_page(page: Path, timeout=180):
    """Opens a test page in headless Chrome on a real clock and waits until its harness has written its results.

    Earlier versions used --virtual-time-budget with --dump-dom. That clock runs ahead of the page's real work on a
    busy machine (GitHub's runners), so a harness could be cut off before it finished.
    """
    started = time.monotonic()
    chrome = DevTools(page.as_uri())
    dom, problem = "", None
    try:
        targets = chrome.call("Target.getTargets")["targetInfos"]
        target = next(t for t in targets if t["type"] == "page")
        chrome.session = chrome.call("Target.attachToTarget", {"targetId": target["targetId"], "flatten": True})[
            "sessionId"]
        while time.monotonic() - started < timeout:
            if chrome.evaluate("!!document.getElementById('lb-results')"):
                dom = chrome.evaluate("document.documentElement.outerHTML") or ""
                break
            time.sleep(0.25)
        else:
            problem = f"no results after {timeout} s"
    except (OSError, RuntimeError, TimeoutError, StopIteration, KeyError, ValueError) as e:  # a failed check
        problem = f"{type(e).__name__}: {e}"
    log = chrome.close()
    m = re.search(r'<pre id="lb-results">(.*?)</pre>', dom, re.DOTALL)
    if not m:
        took = f"{problem or 'no results'}, after {time.monotonic() - started:.1f} s; "
        return [{"name": "harness finished (" + page.name + ")", "ok": False, "info": took + log[-400:]}], dom
    return json.loads(html.unescape(m.group(1))), dom


def main():
    shots = "--screenshots" in sys.argv
    if not CHROMIUM:
        print("litebox-tests: chromium not found")
        return 2
    build_drive()
    before = photo_hashes()
    results = []

    page1 = DRIVE / "test1.html"
    page1.write_text(inject((ROOT / "litebox.html").read_text(encoding="utf-8"), "harness1.js"), encoding="utf-8")
    r1, dom1 = run_page(page1)
    results += r1
    m = re.search(r'<pre id="lb-out">(.*?)</pre>', dom1, re.DOTALL)
    rebuilt = base64.b64decode(html.unescape(m.group(1))).decode("utf-8") if m else None
    results.append({"name": "refresh produced a new litebox.html", "ok": bool(rebuilt), "info": None})

    if rebuilt:
        (DRIVE / "litebox.html").write_text(rebuilt, encoding="utf-8")
        results.append({"name": "rebuilt file has no test harness in it",
                        "ok": "harness1.js" not in rebuilt and "manifest.js" not in rebuilt, "info": None})
        if shots:
            screenshots()
        shutil.move(PHOTOS / "c.png", OUT / "c.png.moved")
        page2 = DRIVE / "test2.html"
        page2.write_text(inject(rebuilt, "harness2.js"), encoding="utf-8")
        r2, _ = run_page(page2)
        results += r2
        shutil.move(OUT / "c.png.moved", PHOTOS / "c.png")

    results.append({"name": "photos unchanged by litebox", "ok": photo_hashes() == before, "info": None})
    src = (ROOT / "litebox.html").read_text(encoding="utf-8")
    results.append({"name": "litebox.html carries its license header",
                    "ok": "Licensed under the Apache License, Version 2.0" in src, "info": None})
    src = re.sub(r"<!--.*?-->", "", src, flags=re.DOTALL)  # comments load nothing (the license header names a web page)
    results.append({"name": "litebox.html names no internet address",
                    "ok": not re.search(r"(https?:)?//[a-z0-9.-]+\.[a-z]{2,}", src, re.IGNORECASE), "info": None})
    results.append({"name": "litebox.html links no outside files",
                    "ok": not re.search(r'<(script|link|img)[^>]+(src|href)=(?!["\']?data:)', src, re.IGNORECASE), "info": None})

    fails = [r for r in results if not r["ok"]]
    for f in fails:
        print("FAIL", f["name"], "—", json.dumps(f.get("info"), ensure_ascii=False))
    print(f"litebox-tests: pass={len(results) - len(fails)} fail={len(fails)}")
    if "--keep" not in sys.argv and not shots and not fails:
        shutil.rmtree(OUT)
    return 0 if not fails else 1


def screenshots():
    viewer = DRIVE / "shot-viewer.html"
    page = (DRIVE / "litebox.html").read_text(encoding="utf-8")
    head, sep, tail = page.rpartition("</body>")
    viewer.write_text(head + "<script>location.hash='all';setTimeout(()=>litebox.open(2),0)</script>" + sep + tail,
                      encoding="utf-8")
    info = DRIVE / "shot-info.html"
    info.write_text(head + "<script>location.hash='album=10%20scans';setTimeout(()=>{litebox.open(0);"
                    "document.getElementById('v-info-btn').click()},0)</script>" + sep + tail, encoding="utf-8")
    setup = DRIVE / "shot-setup.html"
    setup.write_text(head + "<script>location.hash='setup'</script>" + sep + tail, encoding="utf-8")
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-gallery.png"), (DRIVE / "litebox.html").as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-viewer.png"), viewer.as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-info.png"), info.as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-setup.png"), setup.as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-all.png"), (DRIVE / "litebox.html").as_uri() + "#all"])
    chromium(["--virtual-time-budget=5000", "--window-size=390,844",
              "--screenshot=" + str(OUT / "chromium-phone.png"), (DRIVE / "litebox.html").as_uri()])
    firefox = shutil.which("firefox")
    if firefox:
        subprocess.run([firefox, "--headless", "--window-size=1280,800",
                        "--screenshot", str(OUT / "firefox-gallery.png"), (DRIVE / "litebox.html").as_uri()],
                       capture_output=True, timeout=120, check=False)
        subprocess.run([firefox, "--headless", "--window-size=1280,800",
                        "--screenshot", str(OUT / "firefox-viewer.png"), viewer.as_uri()],
                       capture_output=True, timeout=120, check=False)


if __name__ == "__main__":
    sys.exit(main())
