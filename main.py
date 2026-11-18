#!/usr/bin/env python3
"""news-image-20261118 entry: draws a one-page newspaper front page that sums
up the world news of Wednesday 18 November 2026 and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python 3 standard library only: a pixel canvas, a 5x7 bitmap font, filled
map polygons and a small PNG encoder. No network, no randomness, no clock:
two runs write byte-identical files.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 230)
INK = (28, 26, 22)
NAVY = (22, 41, 77)
RED = (179, 38, 30)
OCEAN = (174, 198, 222)
LAND = (217, 198, 155)
LAND_EDGE = (138, 122, 85)
GRATICULE = (158, 182, 208)
DECK = (90, 84, 74)
RULE = (201, 191, 165)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- canvas

canvas = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = color[0]
        canvas[i + 1] = color[1]
        canvas[i + 2] = color[2]


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    r, g, b = color
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            canvas[i] = r
            canvas[i + 1] = g
            canvas[i + 2] = b


def hline(x0, x1, y, color):
    fill_rect(x0, y, x1, y + 1, color)


def vline(x, y0, y1, color):
    fill_rect(x, y0, x + 1, y1, color)


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)


def ring_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        put(cx - dx, cy + dy, color)
        put(cx + dx, cy + dy, color)
        put(cx + dy, cy - dx, color)
        put(cx + dy, cy + dx, color)


def fill_polygon(points, color):
    """Scanline fill of a polygon given as [(x, y), ...] pixel coords."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            fill_rect(int(xs[j]), y, int(xs[j + 1]) + 1, y + 1, color)


def polyline(points, color):
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            put(int(x0 + (x1 - x0) * s / steps),
                int(y0 + (y1 - y0) * s / steps), color)


# ---------------------------------------------------------------- 5x7 font

# Each glyph is 7 rows of 5 characters; '#' is ink, '.' is blank.
FONT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.###", "#..#.", ".##.#"),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '•': (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def clean(text):
    return (text.replace("—", "-").replace("–", "-").replace("’", "'")
                .replace("“", '"').replace("”", '"'))


def text_width(text, scale):
    return len(clean(text)) * 6 * scale


def draw_text(x, y, text, scale, color, align="left"):
    text = clean(text)
    if align == "center":
        x -= text_width(text, scale) // 2
    elif align == "right":
        x -= text_width(text, scale)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + (col + 1) * scale, y + (row + 1) * scale,
                              color)
        cx += 6 * scale
    return cx


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines."""
    text = clean(text)
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- world map

# Simplified continent outlines as (lon, lat) pairs, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-105, 68),
     (-95, 69), (-88, 68), (-82, 66), (-80, 73), (-72, 62), (-65, 60),
     (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 32), (-81, 26), (-84, 30), (-88, 29), (-91, 19), (-94, 18),
     (-97, 16), (-92, 15), (-87, 13), (-83, 9), (-79, 9), (-82, 8),
     (-86, 12), (-90, 14), (-94, 16), (-97, 16), (-101, 18), (-105, 20),
     (-108, 23), (-112, 28), (-115, 30), (-120, 34), (-122, 37), (-124, 42),
     (-124, 48), (-128, 52), (-132, 56), (-137, 58), (-145, 60), (-152, 58),
     (-158, 58), (-162, 58), (-166, 60), (-168, 66)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
     (-35, 78), (-50, 76), (-58, 74), (-55, 70), (-52, 64), (-48, 61)],
    # South America
    [(-79, 9), (-75, 11), (-70, 12), (-64, 10), (-60, 8), (-55, 6),
     (-52, 4), (-50, 0), (-45, -3), (-40, -5), (-35, -8), (-37, -12),
     (-39, -16), (-40, -21), (-46, -24), (-49, -28), (-54, -33), (-58, -35),
     (-62, -39), (-65, -41), (-66, -45), (-68, -50), (-69, -53), (-71, -54),
     (-74, -52), (-73, -46), (-73, -40), (-72, -33), (-71, -28), (-70, -22),
     (-71, -18), (-75, -15), (-78, -10), (-80, -6), (-81, -2), (-80, 2),
     (-78, 6), (-79, 9)],
    # Europe
    [(-10, 38), (-9, 40), (-9, 43), (-4, 44), (-2, 48), (-4, 49), (0, 51),
     (2, 51), (4, 53), (7, 54), (8, 57), (10, 59), (6, 58), (5, 60),
     (10, 62), (14, 64), (18, 66), (22, 69), (26, 71), (30, 70), (33, 68),
     (38, 66), (40, 64), (42, 60), (40, 58), (38, 56), (36, 54), (32, 52),
     (28, 48), (28, 45), (26, 44), (24, 42), (23, 40), (22, 39), (20, 40),
     (19, 42), (16, 44), (13, 45), (10, 44), (8, 44), (4, 43), (2, 42),
     (-1, 40), (-4, 39), (-6, 38), (-9, 39), (-10, 38)],
    # Africa
    [(-6, 33), (-9, 31), (-11, 30), (-14, 28), (-16, 24), (-17, 20),
     (-17, 16), (-16, 12), (-13, 9), (-11, 7), (-8, 5), (-4, 5), (0, 6),
     (5, 6), (9, 4), (10, 2), (12, -1), (13, -4), (12, -8), (13, -12),
     (13, -16), (12, -20), (13, -25), (15, -28), (18, -30), (20, -34),
     (24, -34), (28, -33), (32, -29), (35, -25), (36, -21), (40, -17),
     (40, -12), (41, -8), (42, -3), (45, 0), (48, 2), (51, 3), (51, 10),
     (48, 11), (44, 12), (41, 14), (39, 16), (38, 18), (37, 21), (36, 25),
     (34, 28), (32, 29), (29, 30), (25, 31), (20, 31), (15, 31), (11, 32),
     (8, 32), (4, 34), (0, 34), (-4, 33), (-6, 33)],
    # Asia (mainland, India and south-east Asia included)
    [(28, 71), (35, 68), (42, 68), (50, 69), (58, 69), (66, 70), (72, 71),
     (78, 72), (85, 74), (95, 76), (105, 77), (112, 74), (120, 73),
     (128, 72), (135, 72), (142, 72), (150, 70), (158, 69), (162, 65),
     (170, 66), (178, 65), (178, 62), (172, 60), (164, 60), (160, 56),
     (156, 51), (152, 58), (146, 59), (142, 59), (141, 53), (140, 46),
     (139, 42), (135, 42), (130, 42), (127, 39), (126, 38), (122, 39),
     (120, 35), (122, 31), (120, 27), (118, 25), (114, 22), (110, 20),
     (108, 18), (106, 11), (104, 9), (101, 8), (99, 9), (98, 12), (97, 16),
     (94, 17), (92, 21), (89, 22), (87, 21), (85, 19), (82, 17), (80, 15),
     (78, 9), (76, 8), (74, 13), (72, 20), (70, 22), (67, 24), (63, 25),
     (59, 25), (57, 26), (54, 26), (52, 27), (50, 29), (48, 30), (46, 30),
     (43, 30), (40, 30), (38, 31), (36, 36), (34, 38), (32, 40), (30, 42),
     (28, 44), (28, 48), (28, 52), (30, 56), (30, 60), (30, 64), (28, 68),
     (28, 71)],
    # Arabia
    [(43, 29), (47, 29), (50, 28), (52, 26), (54, 25), (57, 23), (59, 21),
     (58, 19), (56, 17), (54, 15), (51, 14), (48, 13), (45, 12), (43, 13),
     (42, 15), (41, 18), (40, 21), (39, 24), (40, 27), (42, 29)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (116, -35), (119, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (137, -35), (140, -38), (143, -39),
     (146, -39), (150, -37), (153, -32), (153, -27), (151, -24), (148, -20),
     (146, -19), (143, -15), (142, -11), (139, -14), (137, -12), (135, -12),
     (132, -12), (130, -13), (127, -14), (124, -16), (121, -18), (118, -20),
     (115, -21), (113, -22)],
    # United Kingdom
    [(-5, 50), (-4, 52), (-5, 54), (-4, 56), (-3, 58), (-2, 57), (-1, 55),
     (0, 53), (1, 51), (0, 50), (-2, 50), (-4, 50), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (141, 41), (143, 42), (145, 44), (144, 43), (142, 41),
     (141, 38), (139, 36), (137, 35), (135, 34), (132, 33), (130, 31)],
    # Sumatra
    [(95, 5), (97, 4), (99, 2), (101, 0), (103, -2), (105, -4), (106, -6),
     (104, -5), (102, -3), (100, 0), (98, 2), (96, 4), (95, 5)],
    # Borneo
    [(109, 1), (111, 2), (114, 4), (117, 6), (119, 3), (118, 0), (117, -2),
     (115, -3), (112, -3), (110, -2), (109, 0), (109, 1)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -7), (111, -6),
     (108, -6), (105, -6)],
    # New Guinea
    [(131, -1), (134, -2), (137, -2), (140, -3), (143, -4), (146, -6),
     (147, -8), (146, -9), (143, -8), (140, -7), (137, -5), (134, -3),
     (131, -1)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -19), (48, -22), (46, -25),
     (44, -25), (43, -22), (43, -19), (44, -16)],
    # New Zealand
    [(167, -45), (169, -44), (171, -42), (173, -41), (175, -38), (177, -38),
     (176, -40), (174, -41), (172, -43), (170, -44), (168, -46), (167, -45)],
]

# Story pins: (number, lon, lat)
PINS = [
    (1, 121.0, 14.6),    # Manila
    (2, 30.5, 50.4),     # Kyiv
    (3, 50.6, 26.2),     # Bahrain
    (4, 116.4, 39.9),    # Beijing
    (5, -0.1, 51.5),     # London
    (6, 89.0, 15.0),     # Bay of Bengal
    (7, 34.5, 31.5),     # Gaza
    (8, -74.0, 40.7),    # New York
]

# ---------------------------------------------------------------- the news

LEAD_KICKER = "ASIA SUMMIT - MANILA"
LEAD_HEADLINE = ["TRUMP LANDS IN MANILA", "QUAD TALKS, THEN XI"]
LEAD_DECK = ("THE US PRESIDENT OPENS HIS ASIA TOUR AS THE ASEAN SUMMIT "
             "ENDS. A MEETING WITH XI JINPING IS NEXT.")

STORIES = [
    ("MANILA",
     "MODI PUSHES E-VISAS AT ASEAN",
     "INDIA OFFERS FREE E-VISAS AND MARITIME TIES AT THE SUMMIT"),
    ("KYIV",
     "UKRAINE HITS CRIMEA BRIDGE AGAIN",
     "SECOND DAY OF STRIKES AS RUSSIA POUNDS BRIDGES IN KYIV"),
    ("BAHRAIN",
     "IRAN DRONES HIT US RADAR",
     "GULF FORCES ON ALERT AFTER THE ATTACK; BAHRAIN GIVES ALL-CLEAR"),
    ("BEIJING",
     "CANADA, CHINA EXTEND TRADE",
     "XI MEETS CARNEY TO DEEPEN DEALS BEFORE THE APEC SUMMIT"),
    ("LONDON",
     "UK SANCTIONS SETTLEMENT FIRMS",
     "EIGHT FIRMS HIT IN A PUSH TO PROTECT THE TWO-STATE SOLUTION"),
    ("BAY OF BENGAL",
     "CYCLONE AKVAN SET TO TURN SEVERE",
     "STORM STRENGTHENS OVER THE BAY AS INDIA WARNS THE COAST"),
    ("GAZA",
     "AID CHIEFS WARN CEASEFIRE MAY FAIL",
     "WFP: ONE HOT MEAL EVERY TWO DAYS FOR DISPLACED FAMILIES"),
    ("NEW YORK",
     "NVIDIA CHIEF QUITS IN SPY SCANDAL",
     "HUANG STEPS DOWN; CHIP SALES STILL JUMP 103%"),
]

TICKER = ("ALSO TODAY: DHONI RETIRES FROM THE IPL - SPACEX CATCHES A "
          "STARSHIP - UN: 372 CIVILIANS KILLED IN UKRAINE IN OCTOBER - "
          "GRAMMY 2027 NOMINEES OUT - POPE LEO HIT BY ROSARY IN PERU - "
          "BAIDU CHIEF WARNS OF AN AI BUBBLE")

# ---------------------------------------------------------------- layout

MX = 20            # page margin
RX = W - MX        # right edge (1004)
INNER = RX - MX    # 984

fill_rect(0, 0, W, H, PAPER)

# Masthead
fill_rect(MX, 20, RX, 100, NAVY)
draw_text(MX + 16, 32, "THE WORLD", 8, WHITE)
draw_text(RX - 16, 28, "WEDNESDAY", 3, WHITE, align="right")
draw_text(RX - 16, 54, "18 NOVEMBER 2026", 4, WHITE, align="right")
fill_rect(MX, 104, RX, 108, RED)

# Dateline
draw_text(W // 2, 116, "WEDNESDAY 18 NOVEMBER 2026 - THE DAY IN ONE PAGE",
          2, INK, align="center")

# Lead story
draw_text(MX, 140, LEAD_KICKER, 2, RED)
draw_text(MX, 158, LEAD_HEADLINE[0], 5, INK)
draw_text(MX, 196, LEAD_HEADLINE[1], 5, INK)
deck_lines = wrap_text(LEAD_DECK, 2, INNER)
draw_text(MX, 238, deck_lines[0], 2, DECK)
if len(deck_lines) > 1:
    draw_text(MX, 256, deck_lines[1], 2, DECK)

# Map caption
draw_text(MX, 282, "WHERE THE NEWS HAPPENED", 2, INK)
draw_text(RX, 282, "NUMBERS MATCH THE STORIES BELOW", 2, DECK,
          align="right")

# Map panel
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = MX, 300, RX, 522
fill_rect(MAP_X0, MAP_Y0, MAP_X1, MAP_Y1, OCEAN)
MW = MAP_X1 - MAP_X0
MH = MAP_Y1 - MAP_Y0


def lon_to_x(lon):
    return MAP_X0 + int((lon + 180.0) / 360.0 * MW)


def lat_to_y(lat):
    return MAP_Y0 + int((84.0 - lat) / 142.0 * MH)


for lon in range(-180, 181, 60):
    vline(lon_to_x(lon), MAP_Y0, MAP_Y1, GRATICULE)
for lat in range(-60, 91, 30):
    gy = lat_to_y(lat)
    if MAP_Y0 <= gy < MAP_Y1:
        hline(MAP_X0, MAP_X1, gy, GRATICULE)
for poly in CONTINENTS:
    px = [(lon_to_x(lon), lat_to_y(lat)) for lon, lat in poly]
    fill_polygon(px, LAND)
    polyline(px, LAND_EDGE)
for number, lon, lat in PINS:
    cx, cy = lon_to_x(lon), lat_to_y(lat)
    fill_circle(cx, cy, 11, RED)
    ring_circle(cx, cy, 11, WHITE)
    draw_text(cx, cy - 7, str(number), 2, WHITE, align="center")

# Story grid
GRID_Y = 534
CELL_W = 482
CELL_H = 94
GAP_X = 20
GAP_Y = 8
for row in range(4):
    for col in range(2):
        idx = row * 2 + col
        place, headline, deck = STORIES[idx]
        x = MX + col * (CELL_W + GAP_X)
        y = GRID_Y + row * (CELL_H + GAP_Y)
        fill_rect(x, y + 4, x + 30, y + 34, RED)
        draw_text(x + 9, y + 12, str(idx + 1), 2, WHITE)
        draw_text(x + 40, y + 6, place, 2, RED)
        draw_text(x + 40, y + 26, headline, 2, INK)
        deck_wrapped = wrap_text(deck, 2, CELL_W)
        draw_text(x, y + 48, deck_wrapped[0], 2, DECK)
        if len(deck_wrapped) > 1:
            draw_text(x, y + 66, deck_wrapped[1], 2, DECK)
        if col == 0:
            vline(x + CELL_W + GAP_X // 2, y + 4, y + CELL_H, RULE)
    if row < 3:
        hline(MX, RX, GRID_Y + (row + 1) * CELL_H + row * GAP_Y + 4, RULE)

# Ticker: three lines, every item kept
TICK_Y = 946
fill_rect(MX, TICK_Y, RX, TICK_Y + 56, NAVY)
ticker_lines = wrap_text(TICKER, 2, INNER - 16)
for i, line in enumerate(ticker_lines[:3]):
    draw_text(MX + 8, TICK_Y + 4 + i * 17, line, 2, WHITE)

# ---------------------------------------------------------------- PNG encode


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(canvas[y * W * 3:(y + 1) * W * 3])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    assert size <= 1048576, "entry.png over 1 MiB"
    print("WROTE %s %d bytes %dx%d" % (path, size, W, H))


if __name__ == "__main__":
    main()
