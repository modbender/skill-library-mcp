#!/usr/bin/env python3
"""
Monarch Butterfly ANSI Art - drawn via Clawbius API
Reference: https://i.natgeofe.com/k/9acd2bad-fb0e-43a8-935d-ec0aefc60c2f/monarch-butterfly-grass.jpg

Color palette used:
  BLACK (0)  - veins, body, wing borders
  DGREEN (2) - grass background
  BROWN (6)  - main orange wing fill (closest to monarch orange in 16-color)
  DGRAY (8)  - antennae, shadow detail
  YELLOW(14) - bright inner wing glow near body, spots in border
  WHITE (15) - margin dots, body spots
"""

import requests
import os
import sys

BASE = "http://127.0.0.1:7777"

# ---- Color constants ----
BLACK  = 0
DGREEN = 2
BROWN  = 6   # dark orange - main wing color
DGRAY  = 8
YELLOW = 14  # bright amber/inner orange
WHITE  = 15

def post(path, data):
    r = requests.post(f"{BASE}{path}", json=data)
    resp = r.json()
    if not resp.get("ok"):
        print(f"  WARN {path}: {resp}")
    return resp

def draw_at(x, y, code=219, fg=7, bg=0):
    post("/api/draw/at", {"x": x, "y": y, "code": code, "fg": fg, "bg": bg})

def rect(x, y, w, h, code=219, fg=7, bg=0):
    if w <= 0 or h <= 0:
        return
    post("/api/draw/rect/filled", {"x": x, "y": y, "width": w, "height": h,
                                    "code": code, "fg": fg, "bg": bg})

def line(x1, y1, x2, y2, code=219, fg=7, bg=0):
    post("/api/draw/line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2,
                             "code": code, "fg": fg, "bg": bg})

# ============================================================
# CANVAS SETUP
# ============================================================
print("Creating canvas...")
post("/api/file/new", {
    "columns": 80, "rows": 25,
    "title": "Monarch Butterfly",
    "author": "Clawd",
    "group": "ANSIClaw"
})

# Background: dark green grass (light shade on black = grass texture)
print("Drawing grass background...")
rect(0, 0, 80, 25, code=176, fg=DGREEN, bg=BLACK)

# ============================================================
# WING SHAPE DATA
# Each row maps to the OUTERMOST column of that wing
# Left wings: inner edge = col 38, outer edge = these values
# Right wings: inner edge = col 41, outer edge = these values
# Body occupies cols 39-40
# ============================================================

# Left forewing (forewings = top/front wings, larger)
left_fw = {
    2: 30,   # narrow wingtip
    3: 24,
    4: 18,
    5: 13,
    6: 10,
    7: 8,
    8: 7,    # widest (leading edge)
    9: 8,
    10: 9,
    11: 11,
    12: 13,
    13: 16,  # trailing edge
}

# Right forewing (mirror)
right_fw = {
    2: 49,
    3: 55,
    4: 61,
    5: 66,
    6: 69,
    7: 71,
    8: 72,   # widest
    9: 71,
    10: 70,
    11: 68,
    12: 66,
    13: 63,
}

# Left hindwing (smaller, rounder lower wings)
left_hw = {
    13: 22,
    14: 18,
    15: 16,
    16: 15,  # widest
    17: 16,
    18: 17,
    19: 19,
    20: 21,
    21: 24,
    22: 27,
}

# Right hindwing (mirror)
right_hw = {
    13: 57,
    14: 61,
    15: 63,
    16: 64,  # widest
    17: 63,
    18: 62,
    19: 60,
    20: 58,
    21: 55,
    22: 52,
}

# ============================================================
# WING ROW DRAWING FUNCTIONS
# Structure per row: [BLACK border][BROWN orange][YELLOW glow]
# Left wing: border on LEFT (outer tip), glow on RIGHT (near body)
# Right wing: border on RIGHT (outer tip), glow on LEFT (near body)
# ============================================================

def wing_row_left(row, outer, inner=38, tip_w=3, glow_w=5):
    w = inner - outer + 1
    if w <= 0:
        return
    # Outer black border (the wing edge / margin)
    bw = min(tip_w, w)
    rect(outer, row, bw, 1, 219, BLACK, BLACK)
    rem = w - bw
    if rem <= 0:
        return
    # Yellow inner glow near body (rightmost part)
    gw = min(glow_w, rem)
    rect(inner - gw + 1, row, gw, 1, 219, YELLOW, BLACK)
    # Brown orange middle fill
    mid_w = w - bw - gw
    if mid_w > 0:
        rect(outer + bw, row, mid_w, 1, 219, BROWN, BLACK)

def wing_row_right(row, outer, inner=41, tip_w=3, glow_w=5):
    w = outer - inner + 1
    if w <= 0:
        return
    # Outer black border (rightmost)
    bw = min(tip_w, w)
    rect(outer - bw + 1, row, bw, 1, 219, BLACK, BLACK)
    rem = w - bw
    if rem <= 0:
        return
    # Yellow inner glow near body (leftmost)
    gw = min(glow_w, rem)
    rect(inner, row, gw, 1, 219, YELLOW, BLACK)
    # Brown orange middle
    mid_w = w - bw - gw
    if mid_w > 0:
        rect(inner + gw, row, mid_w, 1, 219, BROWN, BLACK)

# ============================================================
# DRAW WINGS (hindwings first, forewings on top)
# ============================================================
print("Drawing hindwings...")
for row, outer in left_hw.items():
    wing_row_left(row, outer, tip_w=2, glow_w=6)
for row, outer in right_hw.items():
    wing_row_right(row, outer, tip_w=2, glow_w=6)

print("Drawing forewings...")
for row, outer in left_fw.items():
    wing_row_left(row, outer, tip_w=3, glow_w=5)
for row, outer in right_fw.items():
    wing_row_right(row, outer, tip_w=3, glow_w=5)

# ============================================================
# BODY
# ============================================================
print("Drawing body...")
# Main body (abdomen) - thin, centered
rect(39, 4, 2, 19, 219, BLACK, BLACK)
# Thorax (slightly wider, rows 9-14)
rect(38, 9, 4, 6, 219, BLACK, BLACK)
# Head area (top of body)
rect(39, 3, 2, 2, 219, BLACK, BLACK)

# White dots on thorax (characteristic monarch marking)
draw_at(39, 5, 254, WHITE, BLACK)
draw_at(40, 5, 254, WHITE, BLACK)
draw_at(38, 11, 254, WHITE, BLACK)
draw_at(41, 11, 254, WHITE, BLACK)

# ============================================================
# VEINS - black lines radiating through the orange
# ============================================================
print("Drawing veins...")

# Left forewing veins
line(38, 5,  22, 3,  219, BLACK, BLACK)  # upper leading vein
line(38, 7,   9, 7,  219, BLACK, BLACK)  # middle leading vein
line(38, 10, 10, 11, 219, BLACK, BLACK)  # lower leading vein
line(38, 13, 18, 10, 219, BLACK, BLACK)  # trailing edge vein

# Left hindwing veins
line(38, 15, 17, 17, 219, BLACK, BLACK)
line(38, 18, 20, 21, 219, BLACK, BLACK)

# Right forewing veins (mirror)
line(41, 5,  57, 3,  219, BLACK, BLACK)
line(41, 7,  70, 7,  219, BLACK, BLACK)
line(41, 10, 69, 11, 219, BLACK, BLACK)
line(41, 13, 61, 10, 219, BLACK, BLACK)

# Right hindwing veins
line(41, 15, 62, 17, 219, BLACK, BLACK)
line(41, 18, 59, 21, 219, BLACK, BLACK)

# ============================================================
# WHITE MARGIN DOTS (the characteristic monarch border spots)
# Two alternating dots along the outer wing edges
# ============================================================
print("Drawing margin dots...")

# Left forewing dots (along outer left edge, every other row)
for row in [3, 5, 7, 9, 11]:
    outer = left_fw.get(row)
    if outer:
        draw_at(outer,     row, 254, WHITE, BLACK)
        draw_at(outer + 1, row, 254, WHITE, BLACK)

# Right forewing dots
for row in [3, 5, 7, 9, 11]:
    outer = right_fw.get(row)
    if outer:
        draw_at(outer,     row, 254, WHITE, BLACK)
        draw_at(outer - 1, row, 254, WHITE, BLACK)

# Left hindwing dots
for row in [14, 16, 18, 20, 22]:
    outer = left_hw.get(row)
    if outer:
        draw_at(outer,     row, 254, WHITE, BLACK)
        draw_at(outer + 1, row, 254, WHITE, BLACK)

# Right hindwing dots
for row in [14, 16, 18, 20, 22]:
    outer = right_hw.get(row)
    if outer:
        draw_at(outer,     row, 254, WHITE, BLACK)
        draw_at(outer - 1, row, 254, WHITE, BLACK)

# Extra inner row of smaller dots (the second dot row)
for row in [4, 6, 8, 10, 12]:
    outer = left_fw.get(row)
    if outer:
        draw_at(outer + 2, row, 249, WHITE, BLACK)
for row in [4, 6, 8, 10, 12]:
    outer = right_fw.get(row)
    if outer:
        draw_at(outer - 2, row, 249, WHITE, BLACK)

# ============================================================
# ORANGE SPOTS in the forewing black border (near wingtips)
# Monarchs have orange patches breaking through the black border
# ============================================================
print("Drawing wingtip orange spots...")

# Left wingtip spots (in the black border area)
draw_at(30, 2, 219, YELLOW, BLACK)
draw_at(31, 2, 219, BROWN,  BLACK)
draw_at(25, 3, 219, YELLOW, BLACK)
draw_at(26, 3, 219, BROWN,  BLACK)
draw_at(19, 4, 219, BROWN,  BLACK)

# Right wingtip spots (mirror)
draw_at(49, 2, 219, YELLOW, BLACK)
draw_at(48, 2, 219, BROWN,  BLACK)
draw_at(54, 3, 219, YELLOW, BLACK)
draw_at(53, 3, 219, BROWN,  BLACK)
draw_at(60, 4, 219, BROWN,  BLACK)

# ============================================================
# ANTENNAE - thin curved lines with club tips
# ============================================================
print("Drawing antennae...")
# Left antenna (curves upper-left)
line(39, 3, 36, 1, 219, DGRAY, BLACK)
draw_at(35, 1, 219, DGRAY, BLACK)   # club knob
draw_at(35, 0, 219, BLACK, BLACK)   # tip

# Right antenna (curves upper-right)
line(40, 3, 43, 1, 219, DGRAY, BLACK)
draw_at(44, 1, 219, DGRAY, BLACK)
draw_at(44, 0, 219, BLACK, BLACK)

# ============================================================
# SAVE & EXPORT
# ============================================================
print("Saving ANS file...")
ans_path = os.path.expanduser("~/Desktop/monarch_butterfly.ans")
result = post("/api/file/save-as", {"path": ans_path})
print(f"  ANS: {result}")

print("Exporting PNG...")
png_path = os.path.expanduser("~/Desktop/monarch_butterfly.png")
result = post("/api/file/export/png", {"path": png_path})
print(f"  PNG: {result}")

print()
print(f"✅ Done!")
print(f"   ANS: {ans_path}")
print(f"   PNG: {png_path}")
