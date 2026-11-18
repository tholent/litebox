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
"""Print the two logo data URLs that litebox.html carries, made from assets/logo.png.

header: the logo as given (white on clear), 84 px, shown at 28 px in the header bar.
icon:   the browser-tab icon, 64 px, with the logo's clear cut-outs filled dark so it
        also shows on a light tab bar.

It also writes assets/logo-dark.png: the logo in near-black, for the README on a light background.

Run: python3 assets/make-logo.py   (needs Pillow)
"""
import base64
import io
import pathlib

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
DARK = (12, 12, 13, 255)  # litebox's --bg


def data_url(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


logo = Image.open(HERE / "logo.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())

# Outside = clear pixels reachable from a corner; everything else is the logo's shape.
mask = logo.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
ImageDraw.floodfill(mask, (0, 0), 128)
shape = mask.point(lambda v: 0 if v == 128 else 255)
filled = Image.new("RGBA", logo.size, (0, 0, 0, 0))
filled.paste(Image.new("RGBA", logo.size, DARK), mask=shape)
filled.alpha_composite(logo)

print("header", data_url(logo.resize((84, 84), Image.LANCZOS)))
print("icon", data_url(filled.resize((64, 64), Image.LANCZOS)))

dark = Image.new("RGBA", logo.size, (26, 26, 28, 255))
dark.putalpha(logo.getchannel("A"))
dark.resize((160, 160), Image.LANCZOS).save(HERE / "logo-dark.png", optimize=True)
