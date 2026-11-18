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
MAP_Y0, MAP_Y1 = 650, 716
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

# (region, headline, summary, icon, tile colour) — the five leads BELOW the
# hero. The #1 story (U.S.–Iran trade fire) lives in the hero panel above.
LEADS = [
    ("ASIA", "APEC OPENS IN SHENZHEN",
     "Trump, Xi and Putin meet Thursday in a first-ever three-way summit.",
     "flags", (31, 107, 74)),
    ("TECH", "NVIDIA BEATS; HUANG NOT COMING BACK",
     "Revenue $115.8B, up 103%; board won't reinstate Huang as CEO; SEC opens a probe.",
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


# ---- Hero illustration: the Strait of Hormuz at dusk ----
# Flat-vector scene, all PIL primitives, fully deterministic. A warship and
# a second vessel on a dark strait, jets overhead, fire and smoke over the
# water, a low sun. Drawn inside (hx, hy, hw, hh); sky occupies the top
# ~58%, sea the rest.
def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_jet_h(d, x, y, s, flip=False):
    """Fighter jet in side profile, drawn on a small layer so it can be
    mirrored cleanly. s = length; flip = faces left."""
    from PIL import Image
    layer = Image.new("RGBA", (s + 24, 44), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    w = (242, 242, 236, 255)
    g = (214, 214, 208, 255)
    # fuselage: long dart, nose right
    ld.polygon([(s + 18, 22), (16, 17), (4, 20), (4, 24), (16, 27)],
               fill=w)
    # swept wing, down-back
    ld.polygon([(s // 2 + 8, 23), (s // 2 - 4, 23), (s // 2 - 20, 42),
                (s // 2 - 8, 42)], fill=g)
    # tail fin, up-back
    ld.polygon([(12, 20), (4, 4), (12, 4), (20, 20)], fill=g)
    # cockpit bump
    ld.ellipse([s - 14, 17, s - 4, 23], fill=(180, 200, 220, 255))
    # flame at the tail
    ld.polygon([(4, 19), (-8, 22), (4, 25)], fill=(255, 210, 63, 255))
    if flip:
        layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
    d._image.paste(layer, (x - 8, y - 22), layer)


def draw_blast(d, cx, cy, r):
    """One explosion sitting on the water: wide orange flame licks, bright
    core, and a tall smoke column rising up-right (never a round 'sun')."""
    # flame licks: three overlapping teardrops
    d.polygon([(cx - r, cy), (cx - r * 0.7, cy - r * 1.1),
               (cx - r * 0.2, cy - r * 0.5), (cx, cy - r * 1.3),
               (cx + r * 0.3, cy - r * 0.5), (cx + r * 0.7, cy - r * 1.0),
               (cx + r, cy), (cx, cy + r * 0.4)], fill=(232, 96, 28))
    d.ellipse([cx - r * 0.62, cy - r * 0.75, cx + r * 0.62, cy + r * 0.25],
              fill=(255, 196, 58))
    d.ellipse([cx - r * 0.32, cy - r * 0.5, cx + r * 0.32, cy + r * 0.2],
              fill=(255, 236, 150))
    # smoke column: puffs rising up-right, darker at the base
    puffs = [(cx + 6, cy - r - 12, 14, (88, 78, 70)),
             (cx + 20, cy - r - 28, 18, (112, 102, 92)),
             (cx + 38, cy - r - 46, 22, (136, 126, 114)),
             (cx + 58, cy - r - 64, 25, (158, 148, 136))]
    for sx, sy, sr, c in puffs:
        d.ellipse([sx - sr, sy - sr * 0.7, sx + sr, sy + sr * 0.7], fill=c)


def draw_hero(d, hx, hy, hw, hh):
    horizon = hy + int(hh * 0.58)
    # sky: crimson -> orange -> gold bands (no sun: the fire is the light)
    stops = [(168, 42, 30), (214, 84, 40), (238, 138, 58), (246, 186, 104)]
    sky_h = horizon - hy
    for i in range(sky_h):
        t = i / max(sky_h - 1, 1)
        seg = t * (len(stops) - 1)
        j = min(int(seg), len(stops) - 2)
        c = _lerp(stops[j], stops[j + 1], seg - j)
        d.line([hx, hy + i, hx + hw - 1, hy + i], fill=c)
    # sea: dark navy with a gold band at the horizon
    d.rectangle([hx, horizon, hx + hw - 1, hy + hh - 1], fill=(14, 34, 62))
    d.line([hx, horizon, hx + hw - 1, horizon], fill=(250, 198, 118), width=2)
    # jets, clear of the smoke: one top-left heading right, one mid-top
    d.line([hx + 16, hy + 30, hx + 96, hy + 26], fill=(255, 255, 255), width=2)
    draw_jet_h(d, hx + 96, hy + 26, 74)
    draw_jet_h(d, hx + 300, hy + 62, 60)
    # small fire glow on the horizon, mid-left
    d.ellipse([hx + 168, horizon - 8, hx + 204, horizon + 6], fill=(240, 120, 40))
    d.ellipse([hx + 178, horizon - 4, hx + 194, horizon + 4], fill=(255, 200, 80))
    # one big explosion over the second vessel, right
    draw_blast(d, hx + 500, horizon + 8, 26)
    # warship, left: hull, superstructure, mast, gun, portholes, wake
    ship = (36, 42, 54)
    deck = (50, 58, 72)
    d.polygon([(hx + 56, horizon + 44), (hx + 236, horizon + 44),
               (hx + 250, horizon + 56), (hx + 238, horizon + 66),
               (hx + 66, horizon + 66), (hx + 52, horizon + 56)], fill=ship)
    d.polygon([(hx + 104, horizon + 44), (hx + 134, horizon + 22),
               (hx + 196, horizon + 22), (hx + 210, horizon + 44)], fill=deck)
    d.polygon([(hx + 148, horizon + 22), (hx + 158, horizon + 4),
               (hx + 182, horizon + 4), (hx + 186, horizon + 22)], fill=deck)
    d.line([hx + 170, horizon + 4, hx + 170, horizon - 14], fill=ship, width=3)
    d.line([hx + 158, horizon - 14, hx + 182, horizon - 14], fill=ship, width=3)
    d.polygon([(hx + 78, horizon + 44), (hx + 96, horizon + 36),
               (hx + 104, horizon + 44)], fill=deck)
    for px in (hx + 118, hx + 142, hx + 166, hx + 190, hx + 214):
        d.ellipse([px - 2, horizon + 52, px + 2, horizon + 56], fill=(255, 210, 100))
    # wake trailing behind the stern, short
    for wy in (horizon + 70, horizon + 78):
        d.line([hx + 12, wy, hx + 56, wy], fill=(120, 160, 195), width=2)
    # second vessel, right, lighter so it reads on the dark sea
    d.polygon([(hx + 440, horizon + 52), (hx + 552, horizon + 52),
               (hx + 560, horizon + 60), (hx + 550, horizon + 68),
               (hx + 448, horizon + 68), (hx + 436, horizon + 60)],
              fill=(62, 70, 86))
    d.polygon([(hx + 478, horizon + 52), (hx + 492, horizon + 38),
               (hx + 518, horizon + 38), (hx + 526, horizon + 52)],
              fill=(74, 82, 98))
    d.line([hx + 502, horizon + 38, hx + 502, horizon + 26], fill=(62, 70, 86), width=2)
    d.line([hx + 440, horizon + 52, hx + 552, horizon + 52], fill=(200, 210, 220), width=2)
    for px in (hx + 470, hx + 500, hx + 530):
        d.ellipse([px - 2, horizon + 58, px + 2, horizon + 62], fill=(255, 210, 100))
    # a few short wave strokes near the hulls
    for wx, wy, wl in ((hx + 300, horizon + 84, 70), (hx + 420, horizon + 92, 90)):
        d.line([wx, wy, wx + wl, wy], fill=(120, 160, 195), width=2)
    # story-1 badge, top-left of the art
    d.ellipse([hx + 10, hy + 10, hx + 34, hy + 34], fill=RED,
              outline=(255, 255, 255), width=2)
    d.text((hx + 22, hy + 21), "1", font=font(BOLD, 14), fill=(255, 255, 255), anchor="mm")


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
    lab_f = font(BOLD, 10)
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


def draw_lead_card(d, x, y, w, h, num, region, headline, summary, icon, tile,
                    head_size, head_lh, sum_size, sum_lh):
    """One lead card. Headline flows first (up to 2 lines); the summary takes
    whatever lines remain — no overflow, no clipping."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=BORDER, width=1)
    d.ellipse([x + 8, y + 8, x + 30, y + 30], fill=RED)
    d.text((x + 19, y + 18), str(num), font=font(BOLD, 14),
           fill=(255, 255, 255), anchor="mm")
    ts = 56 if w < 400 else 60
    tx, ty = x + 38, y + 8
    d.rounded_rectangle([tx, ty, tx + ts, ty + ts], radius=6, fill=tile)
    ICONS[icon](d, tx, ty, ts)
    tx0 = tx + ts + 10
    tw = w - (tx0 - x) - 10
    d.text((tx0, y + 10), region, font=font(BOLD, 12 if w >= 400 else 11), fill=RED)
    head_f = font(DISPB, head_size)
    hy = y + 28 if w < 400 else y + 30
    hlines = wrap(headline, head_f, tw)[:2]
    for ln in hlines:
        d.text((tx0, hy), ln, font=head_f, fill=INK)
        hy += head_lh
    sum_f = font(REG, sum_size)
    sy = hy + 4
    room = (y + h - 4 - sy) // sum_lh
    slines = wrap(summary, sum_f, tw)[:max(room, 0)]
    for ln in slines:
        d.text((tx0, sy), ln, font=sum_f, fill=(60, 60, 58))
        sy += sum_lh
    if len(wrap(headline, head_f, tw)) > 2 or room < 1:
        print("WARN card", num, "headline lines",
              len(wrap(headline, head_f, tw)), "summary room", room)


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- Masthead ----
    d.text((W // 2, 4), "THE WORLD IN ONE PAGE", font=font(DISPBLACK, 38),
           fill=NAVY, anchor="ma")
    date_f = font(BOLD, 14)
    segs = [("WEDNESDAY, 18 NOVEMBER 2026  \u00b7  ", GREY),
            ("30 STORIES", RED),
            ("  \u00b7  ", GREY),
            ("6 CONTINENTS", RED)]
    total = sum(date_f.getlength(t) for t, _ in segs)
    sx = (W - total) // 2
    for t, c in segs:
        d.text((sx, 54), t, font=date_f, fill=c)
        sx += date_f.getlength(t)
    d.rectangle([16, 78, W - 16, 82], fill=RED)
    d.rectangle([16, 85, W - 16, 86], fill=INK)

    # ---- Hero: Gulf illustration + navy headline panel ----
    HY0, HY1 = 92, 326
    draw_hero(d, 16, HY0, 620, HY1 - HY0)
    d.rectangle([636, HY0, 1008, HY1], fill=NAVY)
    d.text((660, 106), "M. EAST  \u00b7  STORY 1", font=font(BOLD, 12),
           fill=(255, 130, 110))
    d.rectangle([660, 130, 984, 132], fill=(255, 210, 63))
    hero_head = font(DISPB, 36)
    hlines = wrap("U.S. AND IRAN TRADE FIRE IN THE GULF", hero_head, 324)
    hy = 140
    for ln in hlines:
        d.text((660, hy), ln, font=hero_head, fill=(255, 255, 255))
        hy += 41
    stand_f = font(REG, 15)
    slines = wrap("U.S. jets strike a missile site on Qeshm after Iran's "
                  "third attack on Bahrain in five days.", stand_f, 324)
    sy = hy + 8
    for ln in slines:
        d.text((660, sy), ln, font=stand_f, fill=(205, 215, 225))
        sy += 18

    # ---- The day's other leads: 3 narrow + 2 wide ----
    ly = 332
    d.rectangle([16, ly + 3, 24, ly + 11], fill=RED)
    d.text((32, ly), "THE DAY'S OTHER LEADS", font=font(BOLD, 14), fill=NAVY)
    d.rectangle([16, ly + 22, W - 16, ly + 24], fill=INK)
    row1_y, row1_h = 360, 128
    for i, (region, headline, summary, icon, tile) in enumerate(LEADS[:3]):
        draw_lead_card(d, 16 + i * 333, row1_y, 325, row1_h, i + 2,
                       region, headline, summary, icon, tile, 17, 21, 13, 15)
    row2_y, row2_h = 496, 132
    for j, (region, headline, summary, icon, tile) in enumerate(LEADS[3:]):
        draw_lead_card(d, 16 + j * 500, row2_y, 492, row2_h, j + 5,
                       region, headline, summary, icon, tile, 24, 28, 14, 17)

    # ---- Map strip ----
    d.text((16, 634), "WHERE THE NEWS HAPPENED", font=font(BOLD, 12), fill=GREY)
    d.text((W - 16, 634), "SIX LEADS, NUMBERED", font=font(BOLD, 12),
           fill=RED, anchor="ra")
    draw_map(d)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=BORDER, width=1)

    # ---- ALSO list ----
    ay = 722
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
            cy += 16
    d.line([508, ly, 508, ly + 12 * 16 - 4], fill=BORDER, width=1)

    # ---- BY THE NUMBERS: dark navy footer band ----
    ny = 944
    d.rectangle([16, ny, W - 16, 1006], fill=NAVY)
    d.rectangle([32, ny + 6, 40, ny + 14], fill=RED)
    d.text((48, ny + 2), "BY THE NUMBERS", font=font(BOLD, 13),
           fill=(255, 255, 255))
    cell_w = 246
    for i, (num, label) in enumerate(NUMBERS):
        cx = 32 + i * cell_w
        if i:
            d.line([cx - 12, ny + 24, cx - 12, ny + 56], fill=(80, 100, 130), width=1)
        d.text((cx, ny + 20), num, font=font(DISPB, 24), fill=(255, 255, 255))
        d.text((cx, ny + 48), label, font=font(REG, 11), fill=(205, 215, 225))

    # ---- Source line ----
    d.text((W // 2, 1008),
           "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera \u00b7 CNN \u00b7 PAHO \u00b7 UNEP \u00b7 UN  \u2014  "
           "Claims marked \u201csays\u201d are unconfirmed. All drawings original.",
           font=font(REG, 11), fill=GREY, anchor="ma")

    page.save(OUT, "PNG", optimize=True)
    import os
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
