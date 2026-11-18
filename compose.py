#!/usr/bin/env python3
"""Compose the news-image-20261118 front page: a PIL-only editorial poster.

One image that sums up Wednesday 18 November 2026: masthead + date + story
count, a numbered world map, six lead cards with flat programmatic icons,
an ALSO one-liner list, a BY THE NUMBERS strip, and a source line.
Fully deterministic (identical bytes on every run), no network, no photos:
every drawing is made here from PIL primitives. All facts were verified
against real reporting on the morning of 18 November 2026 before locking;
disputed claims are hedged. Two claims seen in rival entries were left out
because they could not be verified (Serbia parliament, Kuwait drones).
"""
from PIL import Image, ImageDraw, ImageFont

OUT = "entry.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
# Noto Serif Display — a proper newspaper display face (condensed, high
# contrast). Headlines and masthead use it; body stays DejaVu Sans.
DISPB = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
DISPBLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (11, 29, 51)
RED = (193, 39, 45)
GOLD = (180, 140, 40)
GREY = (90, 90, 86)
CARD = (255, 255, 255)
BORDER = (206, 200, 186)
OCEAN = (203, 224, 234)
LAND = (172, 184, 152)
GRAT = (190, 205, 212)

MAP_X0, MAP_X1 = 16, 1008
MAP_Y0, MAP_Y1 = 112, 198
LON0, LON1 = -170.0, 190.0
LAT0, LAT1 = 72.0, -50.0


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
    return (x, y)


# Simplified continent outlines (lon, lat). Schematic, not survey-grade.
CONTINENTS = [
    ("N. AMERICA", (-100, 52), [
        (-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
        (-105, 70), (-95, 80), (-85, 80), (-78, 73), (-70, 62),
        (-60, 55), (-55, 47), (-60, 44), (-68, 42), (-74, 38),
        (-76, 34), (-80, 27), (-84, 24), (-87, 16), (-92, 15),
        (-95, 18), (-100, 20), (-105, 22), (-112, 28), (-118, 33),
        (-124, 42), (-125, 49), (-132, 56), (-145, 60), (-155, 58),
        (-162, 60), (-168, 66)]),
    ("GREENLAND", (-42, 74), [
        (-55, 60), (-45, 60), (-38, 64), (-30, 68), (-22, 70),
        (-25, 76), (-35, 80), (-48, 79), (-58, 75), (-60, 70)]),
    ("S. AMERICA", (-60, -14), [
        (-80, 10), (-76, 6), (-72, 2), (-70, -2), (-76, -6),
        (-80, -10), (-77, -16), (-72, -20), (-70, -26), (-66, -32),
        (-62, -38), (-58, -44), (-56, -50), (-64, -54), (-68, -52),
        (-70, -46), (-72, -38), (-74, -30), (-76, -22), (-79, -14),
        (-81, -6), (-80, 2), (-80, 10)]),
    ("EUROPE", (0, 62), [
        (-10, 36), (-8, 43), (-2, 47), (0, 50), (4, 53),
        (8, 55), (12, 57), (18, 58), (22, 60), (26, 64),
        (30, 70), (36, 68), (40, 64), (42, 58), (38, 54),
        (32, 50), (28, 46), (24, 44), (20, 42), (16, 40),
        (12, 38), (8, 37), (4, 36), (0, 38), (-5, 36), (-10, 36)]),
    ("AFRICA", (20, 4), [
        (-17, 15), (-12, 28), (-6, 34), (2, 37), (10, 37),
        (18, 33), (26, 32), (32, 31), (36, 28), (40, 18),
        (44, 12), (51, 11), (50, 4), (46, -2), (40, -8),
        (38, -14), (34, -22), (30, -28), (24, -34), (19, -34),
        (16, -28), (13, -18), (11, -8), (9, 2), (6, 5),
        (0, 6), (-6, 5), (-12, 8), (-16, 11), (-17, 15)]),
    ("ASIA", (98, 52), [
        (42, 68), (52, 70), (62, 70), (72, 72), (82, 73),
        (95, 76), (108, 76), (122, 73), (135, 72), (148, 71),
        (160, 69), (172, 66), (178, 65), (170, 60), (162, 56),
        (156, 51), (146, 46), (142, 40), (135, 36), (129, 33),
        (126, 38), (122, 31), (118, 24), (112, 18), (108, 10),
        (104, 8), (100, 12), (96, 16), (92, 21), (88, 22),
        (84, 19), (80, 12), (77, 8), (74, 14), (72, 20),
        (68, 23), (64, 25), (60, 25), (56, 26), (52, 28),
        (50, 30), (47, 30), (44, 34), (42, 38), (40, 42),
        (38, 48), (38, 56), (40, 62), (42, 68)]),
    ("OCEANIA", (134, -25), [
        (113, -22), (114, -28), (118, -33), (124, -33), (130, -32),
        (136, -35), (142, -38), (148, -38), (152, -32), (153, -27),
        (150, -22), (146, -19), (142, -11), (138, -13), (134, -12),
        (130, -13), (126, -14), (122, -16), (118, -20), (113, -22)]),
    ("", (121, 14), [  # Philippines sliver, so the Manila story has land
        (119.5, 18.5), (121.5, 18.5), (122.5, 16.0), (122.0, 12.0),
        (121.0, 9.0), (119.8, 12.0), (119.5, 16.0)]),
]

# (number, lon, lat, display offset px or None)
# Pin 6 (Antalya) is nudged with a leader line: true Antalya sits ~12px
# from the Jerusalem pin, so it is drawn up-left of its true spot.
PINS = [
    (1, 56.5, 26.5, None),    # Qeshm Island / Strait of Hormuz
    (2, 114.1, 22.5, None),   # Shenzhen
    (3, -122.0, 37.4, None),  # Santa Clara (Nvidia)
    (4, 35.2, 31.8, None),    # Jerusalem
    (5, -77.0, 38.9, None),   # Washington DC
    (6, 30.7, 36.9, (28, -14)),  # Antalya (COP31), offset with leader
]

# (region, headline, summary, icon, tile colour)
LEADS = [
    ("M. EAST", "U.S. AND IRAN TRADE FIRE IN THE GULF",
     "U.S. jets strike a missile site on Qeshm after Iran's third attack on Bahrain in five days.",
     "jets", (22, 50, 79)),
    ("ASIA", "APEC OPENS IN SHENZHEN",
     "Trump, Xi and Putin meet Thursday in a first-ever three-way summit.",
     "flags", (31, 107, 74)),
    ("TECH", "NVIDIA BEATS; HUANG NOT COMING BACK",
     "Revenue $115.8B, up 103%; board says it will not reinstate Huang as CEO. SEC opens a probe.",
     "chip", (122, 92, 46)),
    ("M. EAST", "KNESSET ELECTS KAHANA AS SPEAKER",
     "Kahana wins 66-52, a blow to Netanyahu; Eisenkot now tries to form a government.",
     "bank", (44, 68, 98)),
    ("AMERICAS", "U.S. LOSES MEASLES-FREE STATUS",
     "PAHO revokes the status held since 2000; 5,412 cases this year, the most since 1991.",
     "virus", (46, 125, 107)),
    ("CLIMATE", "COP31: 1.5\u00b0C IS GONE",
     "The first COP concedes the Paris target will be overshot; best case now 1.7-1.8 degrees.",
     "thermo", (22, 90, 110)),
]

# (tag, one-liner) — two columns of twelve
ALSO_A = [
    ("M. EAST", "Deutsche Bank slides 6% on 15m-document leak"),
    ("ASIA", "Mongolia's president to resign over $25m claim"),
    ("EUROPE", "Russian An-12 crashes in Kemerovo; 17 feared dead"),
    ("MARKETS", "Brent $92.76 a barrel, down 21% in November"),
    ("TECH", "Anthropic prices IPO today; trades Thu as ANT"),
    ("TECH", "SEC opens probe into Nvidia as board bars Huang"),
    ("M. EAST", "Iran says it downed a U.S. drone near Qeshm"),
    ("M. EAST", "Tanker crew missing after vessel hit twice"),
    ("M. EAST", "Houthi missiles toward Riyadh intercepted"),
    ("AFRICA", "Ebola in DR Congo passes 11,000 cases"),
    ("ASIA", "Japan scrambles jets as Russian planes intrude"),
    ("S. AMERICA", "Pope Leo ends 12-day tour; 1.5m at Lima Mass"),
]
ALSO_B = [
    ("M. EAST", "Third Iranian attack on Bahrain in five days"),
    ("ASIA", "Trump flies to Shenzhen after Manila stop"),
    ("ASIA", "Kim Jong-un's APEC attendance still uncertain"),
    ("CLIMATE", "U.S. sent no official delegation to COP31"),
    ("EUROPE", "Russia says it downed 1,336 drones in a night"),
    ("AMERICAS", "Nvidia shares rise after hours on $130B guide"),
    ("OCEANIA", "Australia co-hosts COP31 with T\u00fcrkiye"),
    ("TECH", "U.S. curbs China's remote access to AI chips"),
    ("M. EAST", "Nearly 4m Syrians have returned since Assad fell"),
    ("EUROPE", "Sweden rejects central facial-biometrics register"),
    ("ASIA", "Bus plunges 100m into a gorge in India; 8 killed"),
    ("S. AMERICA", "Sri Lanka bowled out for 98"),
]

# (big number, label) — labels must fit one line at 12pt in 238px
NUMBERS = [
    ("5,412", "U.S. measles cases in 2026"),
    ("$115.8B", "Nvidia quarterly revenue, up 103%"),
    ("15M", "Deutsche Bank documents leaked"),
    ("1.5\u00b0C", "Paris target COP31 concedes is gone"),
]


def draw_jets(d, x0, y0, s):
    """Fighter jet climbing, white silhouette + flame."""
    w = (255, 255, 255)
    cx = x0 + s // 2
    d.polygon([(cx, y0 + 8), (cx + 6, y0 + 34), (cx + 4, y0 + s - 14),
               (cx - 4, y0 + s - 14), (cx - 6, y0 + 34)], fill=w)
    d.polygon([(cx - 4, y0 + 30), (x0 + 6, y0 + s - 12),
               (x0 + 14, y0 + s - 12)], fill=w)
    d.polygon([(cx + 4, y0 + 30), (x0 + s - 6, y0 + s - 12),
               (x0 + s - 14, y0 + s - 12)], fill=w)
    d.polygon([(cx - 10, y0 + s - 20), (cx - 4, y0 + s - 16),
               (cx - 4, y0 + s - 8), (cx - 10, y0 + s - 8)], fill=w)
    d.polygon([(cx + 10, y0 + s - 20), (cx + 4, y0 + s - 16),
               (cx + 4, y0 + s - 8), (cx + 10, y0 + s - 8)], fill=w)
    d.polygon([(cx - 3, y0 + s - 12), (cx + 3, y0 + s - 12),
               (cx, y0 + s - 2)], fill=(255, 210, 63))


def draw_flags(d, x0, y0, s):
    """Three flag poles with pennants."""
    cols = [(193, 39, 45), (255, 255, 255), (201, 162, 39)]
    for i, c in enumerate(cols):
        px = x0 + 12 + i * 18
        d.line([px, y0 + 10, px, y0 + s - 10], fill=(255, 255, 255), width=3)
        d.polygon([(px, y0 + 10), (px + 15, y0 + 15), (px, y0 + 20)], fill=c)
    d.line([x0 + 6, y0 + s - 8, x0 + s - 6, y0 + s - 8], fill=(255, 255, 255), width=3)


def draw_chip(d, x0, y0, s):
    """Microchip: die, inner core, pins on four sides."""
    w = (255, 255, 255)
    d.rounded_rectangle([x0 + 14, y0 + 14, x0 + s - 14, y0 + s - 14],
                        radius=4, outline=w, width=3)
    d.rectangle([x0 + 24, y0 + 24, x0 + s - 24, y0 + s - 24], fill=w)
    for i in range(3):
        off = 20 + i * 10
        d.line([x0 + off, y0 + 6, x0 + off, y0 + 14], fill=w, width=3)
        d.line([x0 + off, y0 + s - 14, x0 + off, y0 + s - 6], fill=w, width=3)
        d.line([x0 + 6, y0 + off, x0 + 14, y0 + off], fill=w, width=3)
        d.line([x0 + s - 14, y0 + off, x0 + s - 6, y0 + off], fill=w, width=3)


def draw_bank(d, x0, y0, s):
    """Classical bank: pediment, columns, steps."""
    w = (255, 255, 255)
    d.polygon([(x0 + s // 2, y0 + 8), (x0 + 8, y0 + 22), (x0 + s - 8, y0 + 22)], fill=w)
    for cx in (x0 + 14, x0 + s // 2 - 2, x0 + s - 18):
        d.rectangle([cx, y0 + 26, cx + 4, y0 + s - 18], fill=w)
    d.line([x0 + 6, y0 + s - 16, x0 + s - 6, y0 + s - 16], fill=w, width=3)
    d.line([x0 + 6, y0 + s - 10, x0 + s - 6, y0 + s - 10], fill=w, width=3)


def draw_virus(d, x0, y0, s):
    """Virus: spiked circle, inner dots."""
    w = (255, 255, 255)
    cx, cy = x0 + s // 2, y0 + s // 2
    import math
    for k in range(8):
        a = math.pi * k / 4
        x1 = cx + int(16 * math.cos(a))
        y1 = cy + int(16 * math.sin(a))
        x2 = cx + int(24 * math.cos(a))
        y2 = cy + int(24 * math.sin(a))
        d.line([x1, y1, x2, y2], fill=w, width=3)
        d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=w)
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=w)
    d.ellipse([cx - 6, cy - 6, cx - 1, cy - 1], fill=(46, 125, 107))
    d.ellipse([cx + 3, cy + 2, cx + 8, cy + 7], fill=(46, 125, 107))
    d.ellipse([cx - 2, cy + 5, cx + 3, cy + 10], fill=(46, 125, 107))


def draw_thermo(d, x0, y0, s):
    """Thermometer: tube, bulb, mercury, ticks."""
    w = (255, 255, 255)
    cx = x0 + s // 2
    d.rounded_rectangle([cx - 6, y0 + 8, cx + 6, y0 + s - 18], radius=6,
                        outline=w, width=3)
    d.ellipse([cx - 12, y0 + s - 26, cx + 12, y0 + s - 2], fill=(255, 210, 63))
    d.rectangle([cx - 2, y0 + 22, cx + 2, y0 + s - 16], fill=(255, 210, 63))
    for ty in (y0 + 16, y0 + 26, y0 + 36):
        d.line([cx + 6, ty, cx + 12, ty], fill=w, width=2)


ICONS = {"jets": draw_jets, "flags": draw_flags, "chip": draw_chip,
         "bank": draw_bank, "virus": draw_virus, "thermo": draw_thermo}


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=OCEAN)
    # graticule every 30 degrees
    lon = -150
    while lon <= 180:
        x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
        d.line([x, MAP_Y0, x, MAP_Y1], fill=GRAT, width=1)
        lon += 30
    lat = 60
    while lat >= -30:
        y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
        d.line([MAP_X0, y, MAP_X1, y], fill=GRAT, width=1)
        lat -= 30
    for _name, _label, poly in CONTINENTS:
        pts = [project(lo, la) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=(140, 152, 122))
    lab_f = font(BOLD, 11)
    for name, (llo, lla), _poly in CONTINENTS:
        if not name or name == "GREENLAND":
            continue
        lx, ly = project(llo, lla)
        d.text((lx, ly), name, font=lab_f, fill=(88, 96, 80), anchor="mm")
    pin_f = font(BOLD, 13)
    for num, lo, la, off in PINS:
        px, py = project(lo, la)
        dx, dy = px, py
        if off:
            dx, dy = px + off[0], py + off[1]
            d.line([dx, dy, px, py], fill=RED, width=1)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        d.ellipse([dx - 11, dy - 11, dx + 11, dy + 11], fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((dx, dy - 1), str(num), font=pin_f, fill=(255, 255, 255), anchor="mm")


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- Masthead ----
    d.text((W // 2, 8), "THE WORLD IN ONE PAGE", font=font(DISPBLACK, 42),
           fill=NAVY, anchor="ma")
    # Date line: grey date, story counts picked out in red, centered as one unit.
    date_f = font(BOLD, 16)
    segs = [("WEDNESDAY, 18 NOVEMBER 2026  \u00b7  ", GREY),
            ("30 STORIES", RED),
            ("  \u00b7  ", GREY),
            ("6 CONTINENTS", RED)]
    total = sum(date_f.getlength(t) for t, _ in segs)
    sx = (W - total) // 2
    for t, c in segs:
        d.text((sx, 62), t, font=date_f, fill=c)
        sx += date_f.getlength(t)
    d.rectangle([16, 86, W - 16, 90], fill=RED)
    d.rectangle([16, 93, W - 16, 94], fill=INK)

    # ---- Map strip ----
    d.text((16, 98), "WHERE THE NEWS HAPPENED", font=font(BOLD, 12), fill=GREY)
    d.text((W - 16, 98), "SIX LEADS, NUMBERED", font=font(BOLD, 12),
           fill=RED, anchor="ra")
    draw_map(d)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=BORDER, width=1)

    # ---- Lead cards: 2 columns x 3 rows ----
    card_w, card_h, gap = 492, 146, 8
    y0 = 204
    for i, (region, headline, summary, icon, tile) in enumerate(LEADS):
        col, row = i % 2, i // 2
        x = 16 + col * (card_w + gap)
        y = y0 + row * (card_h + gap)
        d.rectangle([x, y, x + card_w, y + card_h], fill=CARD, outline=BORDER, width=1)
        # number badge
        d.ellipse([x + 8, y + 8, x + 30, y + 30], fill=RED)
        d.text((x + 19, y + 18), str(i + 1), font=font(BOLD, 14),
               fill=(255, 255, 255), anchor="mm")
        # icon tile
        tx, ty, ts = x + 40, y + 10, 64
        d.rounded_rectangle([tx, ty, tx + ts, ty + ts], radius=6, fill=tile)
        ICONS[icon](d, tx, ty, ts)
        # text block
        tx0 = x + 116
        d.text((tx0, y + 12), region, font=font(BOLD, 12), fill=RED)
        head_f = font(DISPB, 26)
        lines = wrap(headline, head_f, card_w - 116 - 12)
        hy = y + 30
        for ln in lines[:2]:
            d.text((tx0, hy), ln, font=head_f, fill=INK)
            hy += 31
        sum_f = font(REG, 15)
        slines = wrap(summary, sum_f, card_w - 116 - 12)
        sy = hy + 10
        for ln in slines[:2]:
            d.text((tx0, sy), ln, font=sum_f, fill=(60, 60, 58))
            sy += 18

    # ---- ALSO list ----
    ay = 666
    d.rectangle([16, ay + 3, 24, ay + 11], fill=RED)
    d.text((32, ay), "ALSO ON THIS PAGE", font=font(BOLD, 14), fill=NAVY)
    d.rectangle([16, ay + 22, W - 16, ay + 24], fill=INK)
    tag_f = font(BOLD, 14)
    txt_f = font(REG, 14)
    ly = ay + 30
    for col_items, cx in ((ALSO_A, 16), (ALSO_B, 516)):
        cy = ly
        for tag, text in col_items:
            d.text((cx, cy), tag, font=tag_f, fill=RED)
            tw = tag_f.getlength(tag) + 8
            d.text((cx + tw, cy), text, font=txt_f, fill=INK)
            cy += 17
    d.line([508, ly, 508, ly + 12 * 17 - 4], fill=BORDER, width=1)

    # ---- BY THE NUMBERS ----
    ny = 900
    d.rectangle([16, ny + 3, 24, ny + 11], fill=RED)
    d.text((32, ny), "BY THE NUMBERS", font=font(BOLD, 14), fill=NAVY)
    d.rectangle([16, ny + 22, W - 16, ny + 24], fill=INK)
    cell_w = 246
    for i, (num, label) in enumerate(NUMBERS):
        cx = 16 + i * cell_w
        if i:
            d.line([cx - 8, ny + 30, cx - 8, ny + 30 + 54], fill=BORDER, width=1)
        d.text((cx, ny + 30), num, font=font(DISPB, 28), fill=NAVY)
        lab_f = font(REG, 12)
        llines = wrap(label, lab_f, cell_w - 8)
        ly2 = ny + 66
        for ln in llines[:2]:
            d.text((cx, ly2), ln, font=lab_f, fill=GREY)
            ly2 += 15

    # ---- Source line ----
    d.text((W // 2, 998),
           "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera \u00b7 CNN \u00b7 PAHO \u00b7 UNEP \u00b7 UN  \u2014  "
           "Claims marked \u201csays\u201d are unconfirmed. All drawings original.",
           font=font(REG, 11), fill=GREY, anchor="ma")

    page.save(OUT, "PNG", optimize=True)
    import os
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
