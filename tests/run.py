#!/usr/bin/env python3
"""Test litebox.html end to end in headless Chromium.

Usage: python3 tests/run.py [--screenshots] [--keep]

1. Builds a test drive in tests/out/drive: a copy of litebox.html, a photos/ folder of made-up photos
   (EXIF dates and descriptions, a rotated photo, PNG, WebP, a broken file, formats browsers can't show,
   hidden system files) and files outside photos/ that must be ignored.
2. Run 1 (tests/harness1.js) refreshes the empty litebox from those files and checks the photo list.
3. Run 2 (tests/harness2.js) opens the rebuilt litebox and checks the grid, viewer, keys and slideshow,
   with one photo removed from the drive to check the "not on the drive any more" message.
4. Checks the photos were not changed, and that litebox.html loads nothing from the internet.

Prints any failures, then one line: "litebox-tests: pass=N fail=M". Exit 0 only when fail=0.
--screenshots also writes PNGs of the gallery and viewer (Chromium and Firefox) to tests/out/.
Needs: python3 with Pillow, and chromium (firefox only for --screenshots).
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
OUT = TESTS / "out"
DRIVE = OUT / "drive"
PHOTOS = DRIVE / "photos"
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


def exif_bytes(taken=None, description=None, orientation=None):
    ex = Image.Exif()
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

    files = []
    for p in sorted(DRIVE.rglob("*")):
        if p.is_file():
            files.append({"rel": p.relative_to(DRIVE).as_posix(), "mtime": int(p.stat().st_mtime * 1000)})
    (OUT / "manifest.js").write_text("window.MANIFEST = " + json.dumps({"files": files}) + ";\n")


def photo_hashes():
    return {p.relative_to(PHOTOS).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(PHOTOS.rglob("*")) if p.is_file()}


def inject(page_html: str, harness: str) -> str:
    tag = '<script src="../manifest.js"></script><script src="../../%s"></script>' % harness
    head, sep, tail = page_html.rpartition("</body>")
    return head + tag + sep + tail


def chromium(args):
    cmd = [CHROMIUM, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--allow-file-access-from-files", "--hide-scrollbars"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def run_page(page: Path):
    r = chromium(["--virtual-time-budget=60000", "--window-size=1280,800", "--dump-dom", page.as_uri()])
    m = re.search(r'<pre id="lb-results">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return [{"name": "harness finished (" + page.name + ")", "ok": False,
                 "info": (r.stderr or r.stdout)[-600:]}], r.stdout
    return json.loads(html.unescape(m.group(1))), r.stdout


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
    m = re.search(r'<pre id="lb-out">(.*?)</pre>', dom1, re.S)
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
    results.append({"name": "litebox.html names no internet address",
                    "ok": not re.search(r"(https?:)?//[a-z0-9.-]+\.[a-z]{2,}", src, re.I), "info": None})
    results.append({"name": "litebox.html links no outside files",
                    "ok": not re.search(r'<(script|link|img)[^>]+(src|href)=', src, re.I), "info": None})

    fails = [r for r in results if not r["ok"]]
    for f in fails:
        print("FAIL", f["name"], "—", json.dumps(f.get("info"), ensure_ascii=False))
    print("litebox-tests: pass=%d fail=%d" % (len(results) - len(fails), len(fails)))
    if "--keep" not in sys.argv and not shots and not fails:
        shutil.rmtree(OUT)
    return 0 if not fails else 1


def screenshots():
    viewer = DRIVE / "shot-viewer.html"
    page = (DRIVE / "litebox.html").read_text(encoding="utf-8")
    head, sep, tail = page.rpartition("</body>")
    viewer.write_text(head + "<script>litebox.open(1)</script>" + sep + tail, encoding="utf-8")
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-gallery.png"), (DRIVE / "litebox.html").as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=1280,800",
              "--screenshot=" + str(OUT / "chromium-viewer.png"), viewer.as_uri()])
    chromium(["--virtual-time-budget=5000", "--window-size=390,844",
              "--screenshot=" + str(OUT / "chromium-phone.png"), (DRIVE / "litebox.html").as_uri()])
    firefox = shutil.which("firefox")
    if firefox:
        subprocess.run([firefox, "--headless", "--window-size=1280,800",
                        "--screenshot", str(OUT / "firefox-gallery.png"), (DRIVE / "litebox.html").as_uri()],
                       capture_output=True, timeout=120)
        subprocess.run([firefox, "--headless", "--window-size=1280,800",
                        "--screenshot", str(OUT / "firefox-viewer.png"), viewer.as_uri()],
                       capture_output=True, timeout=120)


if __name__ == "__main__":
    sys.exit(main())
