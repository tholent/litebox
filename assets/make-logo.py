"""Print the two logo data URLs that litebox.html carries, made from assets/logo.png.

header: the logo as given (white on clear), 84 px, shown at 28 px in the header bar.
icon:   the browser-tab icon, 64 px, with the logo's clear cut-outs filled dark so it
        also shows on a light tab bar.

Run: python3 assets/make-logo.py   (needs Pillow)
"""
import base64, io, pathlib
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
