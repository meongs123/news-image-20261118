#!/usr/bin/env python3
"""news-image-20261118: a PIL-only editorial front page for Wednesday 18 Nov 2026.

One image sums up the day: masthead + date + story count, a big hero panel
on the U.S.-Iran trade fire in the Gulf (flat-vector illustration, drawn
here from primitives), five more lead cards, a numbered world map, an ALSO
one-liner list, a BY THE NUMBERS band and a source line.

Everything is drawn with PIL primitives — no photos, no network, no
randomness — so two runs produce byte-identical PNGs. The 30 stories were
verified against real reporting on the morning of 18 November 2026; claims
that could not be verified are hedged ("says"), and two rival claims
(Serbia parliament, Kuwait drones) were left out for lack of verification.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = "entry.png"

# --- typefaces -------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype"
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")
SANS_R = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
# Noto Serif Display: a condensed high-contrast newspaper display face.
# Headlines and the masthead use it; body copy stays DejaVu Sans.
SERIF_B = os.path.join(FONT_DIR, "noto/NotoSerifDisplay-Bold.ttf")
SERIF_X = os.path.join(FONT_DIR, "noto/NotoSerifDisplay-Black.ttf")

# --- palette ---------------------------------------------------------------
PAGE_W, PAGE_H = 1024, 1024
PAPER = (246, 241, 231)      # newsprint
INK = (26, 26, 26)
NAVY = (11, 29, 51)          # hero panel + numbers band
SLATE = (44, 68, 98)         # taste-skill tile blue (never violet)
RED = (193, 39, 45)
GOLD = (180, 140, 40)
GREY = (90, 90, 86)
BODY_GREY = (60, 60, 58)
CARD = (255, 255, 255)
RULE = (206, 200, 186)
SEA = (203, 224, 234)
LAND = (172, 184, 152)
GRID = (190, 205, 212)
MARGIN = 16
RIGHT = PAGE_W - MARGIN

# --- the day's stories (verified facts, hedged where unconfirmed) ---------
HERO_REGION = "M. EAST"
HERO_HEADLINE = "U.S. AND IRAN TRADE FIRE IN THE GULF"
HERO_STANDFIRST = ("U.S. jets strike a missile site on Qeshm after Iran's "
                   "third attack on Bahrain in five days.")

# (region, headline, summary, icon key, tile colour) — leads 2..6, in
# numbered order below the hero.
LEADS = [
    ("ASIA", "APEC OPENS IN SHENZHEN",
     "Trump, Xi and Putin meet Thursday in a first-ever three-way summit.",
     "pennants", (31, 107, 74)),
    ("TECH", "NVIDIA BEATS; HUANG NOT COMING BACK",
     "Revenue $115.8B, up 103%; board won't reinstate Huang as CEO; "
     "SEC opens a probe.",
     "chip", (122, 92, 46)),
    ("M. EAST", "KNESSET ELECTS KAHANA AS SPEAKER",
     "Kahana wins 66-52, a blow to Netanyahu; Eisenkot now tries to form "
     "a government.",
     "bank", SLATE),
    ("AMERICAS", "U.S. LOSES MEASLES-FREE STATUS",
     "PAHO revokes the status held since 2000; 5,412 cases this year, "
     "the most since 1991.",
     "virus", (46, 125, 107)),
    ("CLIMATE", "COP31: 1.5\u00b0C IS GONE",
     "The first COP concedes the Paris target will be overshot; best case "
     "now 1.7-1.8 degrees.",
     "thermo", (22, 90, 110)),
]

# (tag, one-liner) — two columns of twelve, 24 more stories.
ALSO_LEFT = [
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
ALSO_RIGHT = [
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

# (big number, label) — labels fit one line at 11pt inside a 246px cell.
NUMBERS = [
    ("5,412", "U.S. measles cases in 2026"),
    ("$115.8B", "Nvidia quarterly revenue, up 103%"),
    ("15M", "Deutsche Bank documents leaked"),
    ("1.5\u00b0C", "Paris target COP31 concedes is gone"),
]

SOURCE_LINE = ("Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera "
               "\u00b7 CNN \u00b7 PAHO \u00b7 UNEP \u00b7 UN  \u2014  Claims marked "
               "\u201csays\u201d are unconfirmed. All drawings original.")

# --- font cache + text helpers ---------------------------------------------
_faces = {}


def face(path, px):
    """Load a truetype face once and reuse it."""
    key = (path, px)
    if key not in _faces:
        _faces[key] = ImageFont.truetype(path, px)
    return _faces[key]


def fit_lines(text, fnt, width, limit=None):
    """Greedy word wrap: lines that fit `width` in `fnt`, at most `limit`."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if fnt.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if limit is not None:
        lines = lines[:limit]
    return lines


def draw_lines(d, x, y, lines, fnt, fill, leading):
    """Draw stacked lines; return the y just below the last one."""
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def blend(c1, c2, t):
    """Linear blend between two RGB colours."""
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def section_head(d, y, label):
    """Red-square bullet + label + full-width black rule; returns rule y."""
    d.rectangle([MARGIN, y + 3, MARGIN + 8, y + 11], fill=RED)
    d.text((MARGIN + 16, y), label, font=face(SANS_B, 14), fill=NAVY)
    d.rectangle([MARGIN, y + 22, RIGHT, y + 24], fill=INK)
    return y + 24


# --- flat icons for the lead cards -----------------------------------------
# Each draws a white pictogram inside a coloured tile of side `s`,
# anchored at (x, y). All shapes are simple PIL primitives.

def icon_pennants(d, x, y, s):
    """Three flag poles with pennants (summits / diplomacy)."""
    white = (255, 255, 255)
    cols = [RED, white, (201, 162, 39)]
    for i, c in enumerate(cols):
        px = x + 10 + i * 17
        d.line([px, y + 8, px, y + s - 8], fill=white, width=3)
        d.polygon([(px, y + 9), (px + 14, y + 14), (px, y + 19)], fill=c)
    d.line([x + 5, y + s - 7, x + s - 5, y + s - 7], fill=white, width=3)


def icon_chip(d, x, y, s):
    """Microchip: die outline, solid core, pins on all four sides."""
    white = (255, 255, 255)
    d.rounded_rectangle([x + 13, y + 13, x + s - 13, y + s - 13],
                        radius=5, outline=white, width=3)
    d.rectangle([x + 23, y + 23, x + s - 23, y + s - 23], fill=white)
    for i in range(3):
        off = 19 + i * 9
        d.line([x + off, y + 5, x + off, y + 13], fill=white, width=3)
        d.line([x + off, y + s - 13, x + off, y + s - 5], fill=white, width=3)
        d.line([x + 5, y + off, x + 13, y + off], fill=white, width=3)
        d.line([x + s - 13, y + off, x + s - 5, y + off], fill=white, width=3)


def icon_bank(d, x, y, s):
    """Parliament building: pediment, three columns, two steps."""
    white = (255, 255, 255)
    d.polygon([(x + s // 2, y + 7), (x + 7, y + 21), (x + s - 7, y + 21)],
              fill=white)
    for cx in (x + 13, x + s // 2 - 2, x + s - 17):
        d.rectangle([cx, y + 25, cx + 4, y + s - 17], fill=white)
    d.line([x + 5, y + s - 15, x + s - 5, y + s - 15], fill=white, width=3)
    d.line([x + 5, y + s - 9, x + s - 5, y + s - 9], fill=white, width=3)


def icon_virus(d, x, y, s, tile):
    """Virus: spiked ring with a solid core and tile-coloured pores."""
    white = (255, 255, 255)
    cx, cy = x + s // 2, y + s // 2
    for k in range(8):
        a = math.pi * k / 4.0
        x1 = cx + int(15 * math.cos(a))
        y1 = cy + int(15 * math.sin(a))
        x2 = cx + int(23 * math.cos(a))
        y2 = cy + int(23 * math.sin(a))
        d.line([x1, y1, x2, y2], fill=white, width=3)
        d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=white)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=white)
    for ox, oy in ((-5, -5), (4, 3), (-1, 6)):
        d.ellipse([cx + ox - 3, cy + oy - 3, cx + ox + 2, cy + oy + 2],
                  fill=tile)


def icon_thermo(d, x, y, s):
    """Thermometer: tube outline, gold bulb and mercury, three ticks."""
    white = (255, 255, 255)
    gold = (255, 210, 63)
    cx = x + s // 2
    d.rounded_rectangle([cx - 6, y + 7, cx + 6, y + s - 17], radius=6,
                        outline=white, width=3)
    d.ellipse([cx - 11, y + s - 25, cx + 11, y + s - 3], fill=gold)
    d.rectangle([cx - 2, y + 21, cx + 2, y + s - 15], fill=gold)
    for ty in (y + 15, y + 25, y + 35):
        d.line([cx + 6, ty, cx + 12, ty], fill=white, width=2)


ICON_DRAW = {
    "pennants": lambda d, x, y, s, t: icon_pennants(d, x, y, s),
    "chip": lambda d, x, y, s, t: icon_chip(d, x, y, s),
    "bank": lambda d, x, y, s, t: icon_bank(d, x, y, s),
    "virus": lambda d, x, y, s, t: icon_virus(d, x, y, s, t),
    "thermo": lambda d, x, y, s, t: icon_thermo(d, x, y, s),
}


def numbered_disc(d, cx, cy, n, r=11):
    """Red disc with a white number, centred on (cx, cy)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=2)
    d.text((cx, cy - 1), str(n), font=face(SANS_B, 13),
           fill=(255, 255, 255), anchor="mm")


# --- hero illustration: the Strait of Hormuz at dusk -----------------------
# Flat-vector scene inside the box (x0, y0, w, h), all PIL primitives.
# Sky takes the top ~58%, sea the rest. A warship and a second vessel sit
# on dark water, two jets cross the sky with contrails, and one explosion
# throws fire and a smoke column over the second vessel. No sun anywhere:
# the fire is the light.

def hero_jet(d, x, y, length, flip=False):
    """Fighter jet in side profile, nose right (mirrored when flip).
    Drawn directly as polygons: dart fuselage, swept wing, tail fin,
    cockpit bump and a small exhaust flame."""
    white = (242, 242, 236)
    grey = (214, 214, 208)
    nose = x + length
    # fuselage: long dart
    fus = [(nose, y), (x + 14, y - 5), (x + 2, y - 2), (x + 2, y + 2),
           (x + 14, y + 5)]
    # swept wing, trailing down-back
    wing = [(x + length // 2 + 6, y + 1), (x + length // 2 - 6, y + 1),
            (x + length // 2 - 22, y + 20), (x + length // 2 - 10, y + 20)]
    # tail fin, up-back
    fin = [(x + 10, y - 2), (x + 2, y - 18), (x + 10, y - 18),
           (x + 18, y - 2)]
    if flip:
        def mirror(pts):
            return [(2 * x + length - px, py) for px, py in pts]
        fus, wing, fin = mirror(fus), mirror(wing), mirror(fin)
        flame_x = nose
        d.polygon([(x + 2, y - 3), (x - 10, y), (x + 2, y + 3)],
                  fill=(255, 210, 63))
    else:
        flame_x = x + 2
        d.polygon([(x + 2, y - 3), (x - 10, y), (x + 2, y + 3)],
                  fill=(255, 210, 63))
    d.polygon(wing, fill=grey)
    d.polygon(fin, fill=grey)
    d.polygon(fus, fill=white)
    # cockpit bump near the nose
    if flip:
        d.ellipse([nose - 18, y - 5, nose - 8, y + 1], fill=(180, 200, 220))
    else:
        d.ellipse([nose - 18, y - 5, nose - 8, y + 1], fill=(180, 200, 220))


def hero_blast(d, cx, cy, r):
    """Explosion on the water: orange flame licks, bright core, and a
    smoke column drifting up-right in five puffs."""
    # flame: three overlapping teardrops, widest at the base
    d.polygon([(cx - r, cy), (cx - int(r * 0.75), cy - int(r * 1.05)),
               (cx - int(r * 0.25), cy - int(r * 0.45)),
               (cx, cy - int(r * 1.25)),
               (cx + int(r * 0.3), cy - int(r * 0.5)),
               (cx + int(r * 0.7), cy - int(r * 0.95)),
               (cx + r, cy), (cx, cy + int(r * 0.35))],
              fill=(232, 96, 28))
    d.ellipse([cx - int(r * 0.6), cy - int(r * 0.7),
               cx + int(r * 0.6), cy + int(r * 0.25)], fill=(255, 196, 58))
    d.ellipse([cx - int(r * 0.3), cy - int(r * 0.45),
               cx + int(r * 0.3), cy + int(r * 0.2)], fill=(255, 236, 150))
    # smoke: puffs rising up-right, paler as they climb
    puffs = [(cx + 4, cy - r - 10, 13, (84, 74, 66)),
             (cx + 18, cy - r - 26, 17, (106, 96, 86)),
             (cx + 36, cy - r - 44, 21, (130, 120, 108)),
             (cx + 56, cy - r - 62, 24, (152, 142, 130)),
             (cx + 78, cy - r - 78, 27, (172, 162, 150))]
    for sx, sy, sr, col in puffs:
        d.ellipse([sx - sr, sy - int(sr * 0.7), sx + sr, sy + int(sr * 0.7)],
                  fill=col)


def draw_hero_art(d, x0, y0, w, h):
    horizon = y0 + int(h * 0.58)
    # sky: crimson -> orange -> amber bands, row by row
    stops = [(168, 42, 30), (214, 84, 40), (238, 138, 58), (246, 186, 104)]
    sky_h = horizon - y0
    for i in range(sky_h):
        t = i / max(sky_h - 1, 1)
        seg = t * (len(stops) - 1)
        j = min(int(seg), len(stops) - 2)
        d.line([x0, y0 + i, x0 + w - 1, y0 + i],
               fill=blend(stops[j], stops[j + 1], seg - j))
    # sea: deep navy, gold seam on the horizon
    d.rectangle([x0, horizon, x0 + w - 1, y0 + h - 1], fill=(14, 34, 62))
    d.line([x0, horizon, x0 + w - 1, horizon], fill=(250, 198, 118), width=2)
    # jets with contrails, clear of the smoke column
    d.line([x0 + 14, y0 + 28, x0 + 92, y0 + 24], fill=(255, 255, 255), width=2)
    hero_jet(d, x0 + 92, y0 + 24, 72)
    d.line([x0 + 296, y0 + 60, x0 + 352, y0 + 58], fill=(255, 255, 255), width=2)
    hero_jet(d, x0 + 352, y0 + 58, 58)
    # small fire glow on the horizon, mid-left
    d.ellipse([x0 + 170, horizon - 7, x0 + 202, horizon + 5],
              fill=(240, 120, 40))
    d.ellipse([x0 + 180, horizon - 3, x0 + 192, horizon + 3],
              fill=(255, 200, 80))
    # the big explosion, over the second vessel on the right
    hero_blast(d, x0 + 498, horizon + 6, 25)
    # warship, left: raked hull, superstructure, bridge tower, mast,
    # bow gun, gold portholes, short wake
    hull = (36, 42, 54)
    deck = (50, 58, 72)
    d.polygon([(x0 + 54, horizon + 42), (x0 + 234, horizon + 42),
               (x0 + 248, horizon + 54), (x0 + 236, horizon + 64),
               (x0 + 64, horizon + 64), (x0 + 50, horizon + 54)], fill=hull)
    d.polygon([(x0 + 102, horizon + 42), (x0 + 132, horizon + 20),
               (x0 + 194, horizon + 20), (x0 + 208, horizon + 42)], fill=deck)
    d.polygon([(x0 + 146, horizon + 20), (x0 + 156, horizon + 2),
               (x0 + 180, horizon + 2), (x0 + 184, horizon + 20)], fill=deck)
    d.line([x0 + 168, horizon + 2, x0 + 168, horizon - 16], fill=hull, width=3)
    d.line([x0 + 156, horizon - 16, x0 + 180, horizon - 16], fill=hull, width=3)
    d.polygon([(x0 + 76, horizon + 42), (x0 + 94, horizon + 34),
               (x0 + 102, horizon + 42)], fill=deck)
    for px in (x0 + 116, x0 + 140, x0 + 164, x0 + 188, x0 + 212):
        d.ellipse([px - 2, horizon + 50, px + 2, horizon + 54],
                  fill=(255, 210, 100))
    for wy in (horizon + 68, horizon + 76):
        d.line([x0 + 10, wy, x0 + 54, wy], fill=(120, 160, 195), width=2)
    # second vessel, right: lighter hull so it reads on the dark sea
    d.polygon([(x0 + 438, horizon + 50), (x0 + 550, horizon + 50),
               (x0 + 558, horizon + 58), (x0 + 548, horizon + 66),
               (x0 + 446, horizon + 66), (x0 + 434, horizon + 58)],
              fill=(62, 70, 86))
    d.polygon([(x0 + 476, horizon + 50), (x0 + 490, horizon + 36),
               (x0 + 516, horizon + 36), (x0 + 524, horizon + 50)],
              fill=(74, 82, 98))
    d.line([x0 + 500, horizon + 36, x0 + 500, horizon + 24],
           fill=(62, 70, 86), width=2)
    d.line([x0 + 438, horizon + 50, x0 + 550, horizon + 50],
           fill=(200, 210, 220), width=2)
    for px in (x0 + 468, x0 + 498, x0 + 528):
        d.ellipse([px - 2, horizon + 56, px + 2, horizon + 60],
                  fill=(255, 210, 100))
    # short wave strokes near the hulls
    for wx, wy, wl in ((x0 + 298, horizon + 82, 68),
                       (x0 + 418, horizon + 90, 88)):
        d.line([wx, wy, wx + wl, wy], fill=(120, 160, 195), width=2)
    # story-1 badge, top-left of the art
    numbered_disc(d, x0 + 22, y0 + 22, 1, r=12)


# --- world map ---------------------------------------------------------------
# Schematic continent outlines (lon, lat), drawn from memory of world
# geography — not survey-grade, only enough for a reader to place the six
# numbered pins. Equirectangular projection over lon -170..190, lat 75..-55.
MAP_LON = (-170.0, 190.0)
MAP_LAT = (75.0, -55.0)

LANDMASSES = [
    ("N. AMERICA", (-100, 52), [
        (-168, 66), (-156, 71), (-140, 70), (-128, 71), (-120, 72),
        (-108, 69), (-96, 69), (-90, 74), (-82, 73), (-76, 71),
        (-68, 62), (-60, 55), (-55, 47), (-60, 44), (-66, 44),
        (-70, 42), (-74, 39), (-76, 35), (-80, 32), (-81, 26),
        (-84, 30), (-90, 21), (-97, 16), (-92, 14), (-86, 12),
        (-83, 9), (-79, 9), (-77, 7), (-80, 9), (-80, 5),
        (-77, 8), (-80, 12), (-84, 16), (-88, 18), (-90, 21),
        (-97, 26), (-102, 28), (-108, 25), (-114, 29), (-120, 34),
        (-124, 40), (-125, 49), (-132, 56), (-145, 60), (-155, 58),
        (-162, 60), (-168, 66)]),
    ("GREENLAND", (-42, 74), [
        (-58, 64), (-52, 60), (-43, 60), (-32, 68), (-22, 70),
        (-20, 74), (-30, 78), (-45, 80), (-58, 76), (-60, 70)]),
    ("S. AMERICA", (-60, -14), [
        (-77, 8), (-72, 11), (-64, 10), (-60, 8), (-52, 5), (-50, 0),
        (-44, -3), (-35, -8), (-37, -13), (-39, -18), (-41, -23),
        (-48, -28), (-52, -33), (-58, -38), (-62, -41), (-65, -45),
        (-66, -50), (-69, -52), (-70, -55), (-73, -50), (-73, -44),
        (-73, -37), (-72, -30), (-70, -20), (-75, -15), (-80, -10),
        (-81, -5), (-80, 0), (-80, 5), (-77, 8)]),
    ("EUROPE", (10, 60), [
        (-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50),
        (2, 51), (5, 53), (8, 55), (10, 57), (12, 56), (18, 56),
        (21, 55), (21, 59), (24, 60), (28, 62), (30, 66), (30, 70),
        (35, 68), (40, 67), (44, 66), (48, 62), (48, 57), (44, 52),
        (40, 48), (38, 46), (34, 45), (30, 45), (28, 44), (23, 40),
        (19, 42), (15, 44), (12, 44), (8, 44), (3, 42), (0, 40),
        (-2, 37), (-6, 36), (-9, 37)]),
    ("AFRICA", (20, 4), [
        (-17, 15), (-16, 20), (-13, 28), (-9, 32), (-5, 35), (0, 36),
        (10, 37), (11, 34), (19, 32), (25, 32), (32, 31), (35, 28),
        (37, 22), (39, 18), (43, 12), (48, 11), (51, 12), (51, 6),
        (48, 2), (42, -2), (40, -8), (36, -18), (33, -26), (28, -33),
        (20, -35), (17, -32), (15, -27), (13, -18), (12, -10), (9, 4),
        (6, 4), (0, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15)]),
    ("ASIA", (98, 52), [
        (30, 36), (36, 36), (40, 38), (43, 41), (42, 45), (40, 48),
        (38, 52), (40, 56), (42, 60), (44, 64), (50, 66), (55, 68),
        (65, 69), (70, 72), (75, 72), (85, 73), (95, 75), (105, 77),
        (115, 74), (125, 72), (135, 72), (145, 72), (155, 70),
        (162, 68), (170, 66), (178, 65), (172, 62), (162, 58),
        (158, 52), (152, 48), (142, 45), (138, 40), (132, 36),
        (128, 34), (126, 38), (122, 40), (122, 32), (120, 28),
        (116, 22), (110, 18), (108, 10), (104, 8), (100, 8),
        (98, 12), (94, 16), (92, 21), (88, 22), (84, 19), (80, 13),
        (77, 8), (75, 12), (73, 18), (70, 22), (66, 25), (62, 25),
        (58, 26), (54, 27), (52, 29), (50, 30), (48, 30), (44, 29),
        (42, 31), (38, 34), (36, 36), (30, 36)]),
    ("OCEANIA", (134, -25), [
        (114, -22), (114, -30), (118, -34), (124, -33), (130, -32),
        (132, -32), (136, -35), (140, -38), (145, -38), (150, -37),
        (153, -32), (153, -27), (150, -23), (146, -19), (142, -11),
        (138, -15), (135, -12), (132, -12), (129, -14), (126, -14),
        (122, -17), (118, -20), (114, -22)]),
    ("", (0, 0), [  # Borneo
        (109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -3),
        (110, -2)]),
    ("", (0, 0), [  # New Guinea
        (131, -1), (136, -2), (141, -3), (146, -6), (147, -8), (141, -8),
        (136, -6), (131, -3)]),
    ("", (0, 0), [  # Philippines sliver
        (120, 18), (122, 18), (122, 14), (121, 10), (120, 13)]),
]

# (number, lon, lat, display offset in px or None) — one pin per lead.
# Pin 6 (Antalya) sits ~12px from the Jerusalem pin, so it is drawn
# up-left of its true spot with a leader line to the true point.
PINS = [
    (1, 56.3, 26.6, None),     # Qeshm Island / Strait of Hormuz
    (2, 114.1, 22.5, None),    # Shenzhen
    (3, -122.0, 37.4, None),   # Santa Clara (Nvidia)
    (4, 35.2, 31.8, None),     # Jerusalem
    (5, -77.0, 38.9, None),    # Washington DC
    (6, 30.7, 36.9, (28, -14)),  # Antalya (COP31)
]


def make_projector(box):
    """Return a lon/lat -> pixel function for the map box."""
    bx0, by0, bx1, by1 = box
    lon0, lon1 = MAP_LON
    lat0, lat1 = MAP_LAT

    def project(lon, lat):
        px = bx0 + (lon - lon0) / (lon1 - lon0) * (bx1 - bx0)
        py = by0 + (lat0 - lat) / (lat0 - lat1) * (by1 - by0)
        return (px, py)

    return project


def draw_world_map(d, box):
    bx0, by0, bx1, by1 = box
    project = make_projector(box)
    d.rectangle(box, fill=SEA)
    # graticule every 30 degrees
    lon = -150
    while lon <= 180:
        gx, _ = project(lon, 0)
        d.line([gx, by0, gx, by1], fill=GRID, width=1)
        lon += 30
    lat = 60
    while lat >= -30:
        _, gy = project(0, lat)
        d.line([bx0, gy, bx1, gy], fill=GRID, width=1)
        lat -= 30
    for _name, _anchor, poly in LANDMASSES:
        pts = [project(lo, la) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=(140, 152, 122))
    label_f = face(SANS_B, 10)
    for name, (llo, lla), _poly in LANDMASSES:
        if not name or name == "GREENLAND":
            continue
        lx, ly = project(llo, lla)
        d.text((lx, ly), name, font=label_f, fill=(88, 96, 80), anchor="mm")
    for num, lo, la, off in PINS:
        px, py = project(lo, la)
        dx, dy = px, py
        if off is not None:
            dx, dy = px + off[0], py + off[1]
            d.line([dx, dy, px, py], fill=RED, width=1)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        numbered_disc(d, dx, dy, num, r=11)
    d.rectangle(box, outline=RULE, width=1)


# --- lead cards ---------------------------------------------------------------
def draw_lead_card(d, x, y, w, h, num, region, headline, summary, icon, tile):
    """One lead card. The headline flows first (at most 2 lines); the
    summary takes whatever lines remain — nothing is clipped, nothing
    overflows the card."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    numbered_disc(d, x + 19, y + 19, num)
    tile_s = 56
    tx, ty = x + 38, y + 8
    d.rounded_rectangle([tx, ty, tx + tile_s, ty + tile_s], radius=6,
                        fill=tile)
    ICON_DRAW[icon](d, tx, ty, tile_s, tile)
    text_x = tx + tile_s + 10
    text_w = w - (text_x - x) - 10
    narrow = w < 400
    region_px = 11 if narrow else 12
    d.text((text_x, y + 10), region, font=face(SANS_B, region_px), fill=RED)
    head_px = 17 if narrow else 24
    head_lh = 21 if narrow else 28
    head_f = face(SERIF_B, head_px)
    head_y = y + 28 if narrow else y + 30
    head_lines = fit_lines(headline, head_f, text_w, limit=2)
    hy = draw_lines(d, text_x, head_y, head_lines, head_f, INK, head_lh)
    sum_px = 13 if narrow else 14
    sum_lh = 15 if narrow else 17
    sum_f = face(SANS_R, sum_px)
    room = (y + h - 4 - (hy + 4)) // sum_lh
    sum_lines = fit_lines(summary, sum_f, text_w, limit=max(room, 0))
    draw_lines(d, text_x, hy + 4, sum_lines, sum_f, BODY_GREY, sum_lh)
    if len(fit_lines(headline, head_f, text_w)) > 2 or room < 1:
        print("WARN card", num, "headline lines",
              len(fit_lines(headline, head_f, text_w)), "summary room", room)


# --- page assembly ------------------------------------------------------------
def draw_masthead(d):
    d.text((PAGE_W // 2, 4), "THE WORLD IN ONE PAGE",
           font=face(SERIF_X, 38), fill=NAVY, anchor="ma")
    date_f = face(SANS_B, 14)
    segs = [("WEDNESDAY, 18 NOVEMBER 2026  \u00b7  ", GREY),
            ("30 STORIES", RED),
            ("  \u00b7  ", GREY),
            ("6 CONTINENTS", RED)]
    total = sum(date_f.getlength(t) for t, _ in segs)
    sx = (PAGE_W - total) // 2
    for text, col in segs:
        d.text((sx, 54), text, font=date_f, fill=col)
        sx += date_f.getlength(text)
    d.rectangle([MARGIN, 78, RIGHT, 82], fill=RED)
    d.rectangle([MARGIN, 85, RIGHT, 86], fill=INK)


def draw_hero(d):
    hy0, hy1 = 92, 326
    draw_hero_art(d, MARGIN, hy0, 620, hy1 - hy0)
    d.rectangle([636, hy0, RIGHT, hy1], fill=NAVY)
    d.text((660, 106), HERO_REGION + "  \u00b7  STORY 1",
           font=face(SANS_B, 12), fill=(255, 130, 110))
    d.rectangle([660, 130, 984, 132], fill=(255, 210, 63))
    head_f = face(SERIF_B, 36)
    head_lines = fit_lines(HERO_HEADLINE, head_f, 324)
    hy = draw_lines(d, 660, 140, head_lines, head_f, (255, 255, 255), 41)
    stand_f = face(SANS_R, 15)
    stand_lines = fit_lines(HERO_STANDFIRST, stand_f, 324)
    draw_lines(d, 660, hy + 8, stand_lines, stand_f, (205, 215, 225), 18)


def draw_leads(d):
    section_head(d, 334, "THE DAY'S OTHER LEADS")
    row1_y, row1_h = 362, 128
    for i, (region, headline, summary, icon, tile) in enumerate(LEADS[:3]):
        draw_lead_card(d, MARGIN + i * 333, row1_y, 325, row1_h, i + 2,
                       region, headline, summary, icon, tile)
    row2_y, row2_h = 498, 132
    for j, (region, headline, summary, icon, tile) in enumerate(LEADS[3:]):
        draw_lead_card(d, MARGIN + j * 500, row2_y, 492, row2_h, j + 5,
                       region, headline, summary, icon, tile)


def draw_map_strip(d):
    d.text((MARGIN, 632), "WHERE THE NEWS HAPPENED",
           font=face(SANS_B, 12), fill=GREY)
    d.text((RIGHT, 632), "SIX LEADS, NUMBERED",
           font=face(SANS_B, 12), fill=RED, anchor="ra")
    draw_world_map(d, (MARGIN, 646, RIGHT, 718))


def draw_also(d):
    section_head(d, 724, "ALSO ON THIS PAGE")
    tag_f = face(SANS_B, 14)
    txt_f = face(SANS_R, 14)
    top = 752
    for items, cx in ((ALSO_LEFT, MARGIN), (ALSO_RIGHT, 516)):
        cy = top
        for tag, text in items:
            d.text((cx, cy), tag, font=tag_f, fill=RED)
            d.text((cx + tag_f.getlength(tag) + 8, cy), text,
                   font=txt_f, fill=INK)
            cy += 15
    d.line([508, top, 508, top + 12 * 15 - 4], fill=RULE, width=1)


def draw_numbers(d):
    ny = 940
    d.rectangle([MARGIN, ny, RIGHT, 1000], fill=NAVY)
    d.rectangle([MARGIN + 16, ny + 6, MARGIN + 24, ny + 14], fill=RED)
    d.text((MARGIN + 32, ny + 2), "BY THE NUMBERS",
           font=face(SANS_B, 13), fill=(255, 255, 255))
    cell_w = 246
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + 16 + i * cell_w
        if i:
            d.line([cx - 12, ny + 24, cx - 12, ny + 56],
                   fill=(80, 100, 130), width=1)
        d.text((cx, ny + 20), num, font=face(SERIF_B, 24),
               fill=(255, 255, 255))
        d.text((cx, ny + 46), label, font=face(SANS_R, 11),
               fill=(205, 215, 225))


def build():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)
    draw_masthead(d)
    draw_hero(d)
    draw_leads(d)
    draw_map_strip(d)
    draw_also(d)
    draw_numbers(d)
    d.text((PAGE_W // 2, 1003), SOURCE_LINE, font=face(SANS_R, 11),
           fill=GREY, anchor="ma")
    return page


def main():
    page = build()
    page.save(OUT, "PNG", optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
