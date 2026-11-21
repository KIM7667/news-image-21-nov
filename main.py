#!/usr/bin/env python3
"""The World Today - 21 November 2026.

A pure-stdlib Python program that draws a newspaper front page summing
up the world news of Saturday, 21 November 2026 as one 1024x1024 PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
No network, no third-party packages, deterministic: two runs produce
identical bytes.

Lead + six verified stories of 21 November 2026:
  Lead: Russian missiles land in Poland - two Russian missiles and a
    suspected drone came down in Poland; Poland calls it a deliberate
    provocation, NATO calls it a grave violation of its airspace.
  1. Markets: US stocks plunge about 3.7%; the S&P 500 and the Dow
    enter correction territory as AI shares sell off.
  2. The Hague: the International Court of Justice rules Myanmar
    committed genocide against the Rohingya.
  3. India: Cyclone Akvan crosses the Odisha coast near Gopalpur;
    about 300,000 people evacuated, heavy rain.
  4. Brussels: the UK and the EU sign deals on food trade, carbon
    markets and youth mobility.
  5. Gaza: Australia, Canada, Italy and the UK jointly call on Israel
    to let aid reach flooded Gaza.
  6. Brazil: imprisoned ex-president Jair Bolsonaro taken to hospital
    with severe abdominal pain.
Footer: France sees a fourth weekend of cost-of-living protests;
Israel's president taps Eisenkot to form a government, bypassing
Netanyahu; NSE becomes the world's 5th-largest listed exchange.
"""

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

PAPER = (248, 244, 236)
INK = (18, 18, 18)
RED = (176, 32, 32)
BLUE = (28, 62, 118)
SKY = (190, 210, 228)
SEA = (52, 104, 158)
LEAF = (150, 185, 120)
GOLD = (198, 160, 40)
GREY = (96, 96, 96)
PALE = (233, 227, 213)
ORANGE = (226, 116, 54)
TEAL = (24, 120, 112)
NAVY = (24, 38, 68)

# ------------------------------------------------------------------ font
# 5x7 bitmap glyphs. Each glyph is seven integers; each integer holds
# one row as five bits, most significant bit on the left.
GLYPHS = {
    'A': (14, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (14, 17, 16, 23, 17, 17, 15),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 27, 17),
    'X': (17, 17, 10, 4, 10, 17, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 6, 8, 16, 31),
    '3': (31, 2, 4, 2, 1, 17, 14),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (6, 8, 16, 30, 17, 17, 14),
    '7': (31, 1, 2, 4, 8, 8, 8),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 2, 12),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 12, 4, 8),
    ':': (0, 12, 12, 0, 12, 12, 0),
    ';': (0, 12, 12, 0, 12, 4, 8),
    '-': (0, 0, 0, 14, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '!': (4, 4, 4, 4, 4, 0, 4),
    '?': (14, 17, 1, 6, 4, 0, 4),
    '/': (1, 2, 2, 4, 8, 8, 16),
    '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
    '$': (4, 15, 20, 14, 5, 30, 4),
    '%': (25, 26, 2, 4, 8, 11, 19),
    '&': (12, 18, 20, 8, 21, 18, 13),
    '+': (0, 4, 4, 14, 4, 4, 0),
    '=': (0, 0, 31, 0, 31, 0, 0),
    '"': (10, 10, 0, 0, 0, 0, 0),
    '*': (0, 4, 21, 14, 21, 4, 0),
}


def text_w(s, scale):
    """Pixel width of s rendered at the given scale."""
    return len(s) * 6 * scale - scale


def wrap_text(s, width_chars):
    """Greedy word wrap; returns lines of at most width_chars chars."""
    out, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > width_chars:
            out.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ page
class Page:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, c)

    def hbar(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vbar(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= (r + t) ** 2:
                    self.dot(xx, yy, c)

    def oval(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.dot(xx, yy, c)

    def seg(self, x0, y0, x1, y1, c):
        """Bresenham line segment."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        """Scanline-filled polygon."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.dot(x, y, c)

    def glyph(self, ch, x, y, scale, c):
        rows = GLYPHS.get(ch.upper(), GLYPHS['?'])
        for r in range(7):
            bits = rows[r]
            for col in range(5):
                if bits >> (4 - col) & 1:
                    self.fill(x + col * scale, y + r * scale,
                              scale, scale, c)

    def put(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, c)
            cx += 6 * scale
        return cx

    def put_mid(self, s, cx, y, scale, c):
        self.put(s, cx - text_w(s, scale) // 2, y, scale, c)

    def para(self, s, x, y, width, scale, c, leading=None):
        if leading is None:
            leading = 9 * scale
        chars = max(1, width // (6 * scale))
        lines = wrap_text(s, chars)
        for i, line in enumerate(lines):
            self.put(line, x, y + i * leading, scale, c)
        return len(lines)


def bezier_dots(pg, p0, pc, p1, c, step=0.02):
    """Dotted quadratic bezier arc (dashed missile trail)."""
    n = 0
    t = 0.0
    while t <= 1.0:
        u = 1.0 - t
        x = int(u * u * p0[0] + 2 * u * t * pc[0] + t * t * p1[0])
        y = int(u * u * p0[1] + 2 * u * t * pc[1] + t * t * p1[1])
        if n % 3 == 0:
            pg.disc(x, y, 2, c)
        n += 1
        t += step


# ------------------------------------------------------------- tile icons
def icon_chart(pg, x, y, col):
    pg.fill(x, y, 2, 36, col)
    pg.hbar(x, y + 34, 40, col)
    pg.seg(x + 5, y + 8, x + 13, y + 14, col)
    pg.seg(x + 13, y + 14, x + 20, y + 11, col)
    pg.seg(x + 20, y + 11, x + 27, y + 22, col)
    pg.seg(x + 27, y + 22, x + 35, y + 30, col)
    pg.disc(x + 5, y + 8, 2, col)
    pg.poly([(x + 35, y + 30), (x + 28, y + 28), (x + 33, y + 23)], col)


def icon_court(pg, x, y, col):
    pg.poly([(x + 2, y + 12), (x + 38, y + 12), (x + 20, y + 2)], col)
    pg.fill(x + 7, y + 14, 4, 18, col)
    pg.fill(x + 18, y + 14, 4, 18, col)
    pg.fill(x + 29, y + 14, 4, 18, col)
    pg.hbar(x + 2, y + 34, 36, col)


def icon_cyclone(pg, x, y, col):
    pg.ring(x + 20, y + 18, 15, col, 2)
    pg.ring(x + 20, y + 18, 10, col, 2)
    pg.ring(x + 20, y + 18, 5, col, 2)
    pg.disc(x + 20, y + 18, 2, col)
    pg.seg(x + 4, y + 34, x + 14, y + 30, col)
    pg.seg(x + 26, y + 34, x + 36, y + 30, col)


def icon_flags(pg, x, y, col):
    # Union Jack, simplified: white field, red cross.
    pg.fill(x, y + 4, 18, 12, PAPER)
    pg.box(x, y + 4, 18, 12, INK, 1)
    pg.fill(x + 8, y + 4, 3, 12, RED)
    pg.fill(x, y + 9, 18, 3, RED)
    # EU flag: blue field, ring of gold stars.
    pg.fill(x + 22, y + 4, 18, 12, BLUE)
    pg.box(x + 22, y + 4, 18, 12, INK, 1)
    for dx, dy in ((4, 0), (2, 3), (-2, 3), (-4, 0), (-2, -3), (2, -3)):
        pg.disc(x + 31 + dx, y + 10 + dy, 1, GOLD)


def icon_aid(pg, x, y, col):
    pg.box(x + 6, y + 8, 28, 20, col, 2)
    pg.fill(x + 18, y + 13, 4, 10, RED)
    pg.fill(x + 13, y + 16, 14, 4, RED)
    pg.fill(x + 4, y + 33, 16, 2, BLUE)
    pg.fill(x + 20, y + 37, 16, 2, BLUE)


def icon_clinic(pg, x, y, col):
    pg.ring(x + 20, y + 20, 16, col, 2)
    pg.fill(x + 17, y + 10, 6, 20, RED)
    pg.fill(x + 10, y + 17, 20, 6, RED)


# ------------------------------------------------------------------ page
def draw_page():
    pg = Page(W, H, PAPER)
    pg.box(10, 10, W - 20, H - 20, INK, 3)
    pg.box(18, 18, W - 36, H - 36, INK, 1)

    # Masthead
    pg.put_mid("THE WORLD TODAY", W // 2, 34, 6, INK)
    pg.hbar(48, 92, W - 96, INK)
    pg.hbar(48, 96, W - 96, INK)
    pg.put_mid("SATURDAY 21 NOVEMBER 2026 - THE DAY IN WORLD NEWS",
               W // 2, 108, 2, RED)

    # ---- lead art: map of Poland, missile trails, NATO star ---------
    px0, py0, pw, ph = 40, 138, 944, 236
    pg.box(px0, py0, pw, ph, INK, 2)
    pg.fill(px0 + 2, py0 + 2, pw - 4, ph - 4, SKY)
    # Poland, rough outline.
    poland = [(150, 175), (235, 158), (320, 166), (405, 182), (455, 205),
              (448, 252), (425, 298), (375, 330), (295, 342), (215, 332),
              (158, 298), (128, 248), (132, 202)]
    pg.poly(poland, LEAF)
    for i in range(len(poland)):
        x0, y0 = poland[i]
        x1, y1 = poland[(i + 1) % len(poland)]
        pg.seg(x0, y0, x1, y1, NAVY)
        pg.seg(x0, y0 + 1, x1, y1 + 1, NAVY)
    # missile trails arcing in from the east, impact markers, drone.
    bezier_dots(pg, (540, 185), (500, 225), (388, 272), RED)
    bezier_dots(pg, (540, 250), (470, 215), (330, 238), RED)
    pg.disc(330, 238, 9, RED)
    pg.ring(330, 238, 13, RED, 2)
    pg.disc(388, 272, 9, RED)
    pg.ring(388, 272, 13, RED, 2)
    pg.poly([(355, 196), (347, 210), (363, 210)], INK)
    pg.put_mid("POLAND", 290, 352, 2, NAVY)
    # NATO compass star.
    pg.disc(755, 245, 68, BLUE)
    pg.ring(755, 245, 68, NAVY, 3)
    pg.poly([(755, 183), (768, 232), (817, 245), (768, 258),
             (755, 307), (742, 258), (693, 245), (742, 232)], PAPER)
    pg.disc(755, 245, 13, NAVY)
    pg.disc(755, 245, 5, PAPER)
    pg.put_mid("NATO", 755, 326, 3, NAVY)
    pg.put_mid("ALLIES ON ALERT", 755, 356, 1, NAVY)

    # ---- lead headline + deck ---------------------------------------
    pg.put_mid("RUSSIAN MISSILES LAND IN POLAND", W // 2, 396, 4, INK)
    pg.put_mid("NATO CALLS IT A GRAVE VIOLATION", W // 2, 432, 4, RED)
    deck = ("Two Russian missiles and a suspected drone came down in "
            "Poland. Warsaw calls it a deliberate provocation; NATO calls "
            "it a grave violation of its airspace.")
    pg.para(deck, 112, 478, 800, 2, INK)
    pg.hbar(48, 552, W - 96, INK)
    pg.hbar(48, 556, W - 96, INK)

    # ---- story grid --------------------------------------------------
    stories = [
        ("MARKETS", "US STOCKS PLUNGE 3.7%; S&P 500 AND DOW ENTER CORRECTION",
         "Wall Street sells off as AI shares slide; the S and P 500 and "
         "the Dow fall into correction.", RED, icon_chart),
        ("THE HAGUE", "ICJ RULES MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA",
         "The Hague court finds Myanmar committed genocide against the "
         "Rohingya minority.", BLUE, icon_court),
        ("INDIA", "CYCLONE AKVAN CROSSES ODISHA COAST; 300,000 EVACUATED",
         "Akvan makes landfall near Gopalpur with heavy rain; about "
         "300,000 people moved to safety.", TEAL, icon_cyclone),
        ("BRUSSELS", "UK AND EU SIGN DEALS ON FOOD, CARBON AND YOUTH MOBILITY",
         "Brussels agreements cover food trade, carbon markets and youth "
         "mobility schemes.", GOLD, icon_flags),
        ("GAZA", "FOUR ALLIES URGE ISRAEL TO LET AID REACH FLOODED GAZA",
         "Australia, Canada, Italy and the UK jointly call for aid to "
         "reach flooded Gaza.", ORANGE, icon_aid),
        ("BRAZIL", "JAILED BOLSONARO TAKEN TO HOSPITAL WITH SEVERE PAIN",
         "Brazil's imprisoned ex-president is rushed to hospital with "
         "severe abdominal pain.", NAVY, icon_clinic),
    ]
    gx0, gy0 = 40, 576
    tw, th = 464, 118
    for i, (kicker, head, body, accent, icon) in enumerate(stories):
        x = gx0 + (i % 2) * (tw + 16)
        y = gy0 + (i // 2) * (th + 12)
        pg.fill(x, y, 6, th, accent)
        pg.put(kicker, x + 16, y + 2, 2, accent)
        icon(pg, x + tw - 48, y + 4, accent)
        pg.para(head, x + 16, y + 22, tw - 16 - 56, 2, INK)
        pg.para(body, x + 16, y + 62, tw - 16, 2, GREY)
        pg.hbar(x, y + th - 1, tw, PALE)

    # ---- footer ------------------------------------------------------
    pg.hbar(48, 966, W - 96, INK)
    foot1 = ("ALSO: FRANCE SEES A FOURTH WEEKEND OF COST-OF-LIVING "
             "PROTESTS")
    foot2 = ("EISENKOT TAPPED TO FORM ISRAEL'S GOVERNMENT - NSE NOW "
             "WORLD'S 5TH-LARGEST EXCHANGE")
    pg.put_mid(foot1, W // 2, 978, 1, INK)
    pg.put_mid(foot2, W // 2, 992, 1, INK)
    return pg


def png_chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def save_png(pg, path):
    raw = b"".join(b"\x00" + bytes(pg.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + png_chunk(b"IDAT", zlib.compress(raw, 9))
           + png_chunk(b"IEND", b""))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size = save_png(draw_page(), os.path.join(out, "entry.png"))
    print(f"wrote entry.png {size} bytes")


if __name__ == "__main__":
    main()
