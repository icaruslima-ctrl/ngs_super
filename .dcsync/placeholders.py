#!/usr/bin/env python3
"""Generate stand-ins for the four assets the DesignSync 256 KiB cap truncated.

These are deliberately obvious placeholders, not reconstructions. Replace them
with the real files from the Claude Design project and the page is complete.
"""
import struct
import zlib

SVG = """<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{w}" height="{h}" rx="16" fill="{fill}"/>
  <rect x="4" y="4" width="{iw}" height="{ih}" rx="12" fill="none"
        stroke="{stroke}" stroke-width="2" stroke-dasharray="8 6"/>
  <text x="50%" y="47%" text-anchor="middle" font-family="Helvetica, Arial, sans-serif"
        font-size="13" font-weight="700" fill="{stroke}">PLACEHOLDER</text>
  <text x="50%" y="59%" text-anchor="middle" font-family="Helvetica, Arial, sans-serif"
        font-size="10" fill="{stroke}">{label}</text>
</svg>
"""


def write_svg(path, w, h, fill, stroke, label):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(SVG.format(w=w, h=h, iw=w - 8, ih=h - 8, fill=fill, stroke=stroke, label=label))
    print(f"{path}  ({w}x{h})")


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, w, h, rgb):
    """Minimal solid-colour 8-bit RGB PNG with a dashed-looking border band."""
    border = tuple(max(0, c - 40) for c in rgb)
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter type 0
        for x in range(w):
            edge = x < 3 or y < 3 or x >= w - 3 or y >= h - 3
            raw.extend(border if edge else rgb)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"{path}  ({w}x{h})")


write_svg("assets/icon-working.svg", 172, 172, "#fdf1f0", "#c98b8c", "icon-working")
write_svg("assets/icon-in-retirement.svg", 172, 172, "#eaf6ec", "#5a9b6d", "icon-in-retirement")
write_png("assets/quiz-photo.png", 538, 538, (232, 243, 233))
write_png("assets/lost-super-photo.png", 521, 500, (247, 242, 236))
