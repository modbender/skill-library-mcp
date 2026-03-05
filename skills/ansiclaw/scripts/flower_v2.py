import requests

BASE = "http://127.0.0.1:7777"

def post(path, data):
    r = requests.post(f"{BASE}{path}", json=data)
    resp = r.json()
    if not resp.get("ok"):
        print(f"WARN {path}: {resp}")
    return resp

def at(x, y, code=219, fg=7, bg=0):
    post("/api/draw/at", {"x": x, "y": y, "code": code, "fg": fg, "bg": bg})

def rect(x, y, w, h, code=219, fg=7, bg=0):
    if w > 0 and h > 0:
        post("/api/draw/rect/filled", {"x": x, "y": y, "width": w, "height": h,
                                        "code": code, "fg": fg, "bg": bg})

# Block codes
F1, F2, F3, F4 = 176, 177, 178, 219
UH  = 223  # upper half ▀
LH  = 220  # lower half ▄
LFH = 221  # left half  ▌
RFH = 222  # right half ▐

# Colors (ice colors OFF — bg must be 0-7 only)
BLACK  = 0; DBLUE  = 1; DGREEN = 2; DCYAN  = 3
DRED   = 4; DMAG   = 5; BROWN  = 6; LGRAY  = 7
DGRAY  = 8; BLUE   = 9; GREEN  = 10; CYAN  = 11
RED    = 12; LMAG  = 13; YELLOW = 14; WHITE = 15

# New canvas — ice colors OFF
post("/api/file/new", {
    "columns": 80, "rows": 25,
    "title": "Flower", "author": "Clawd", "group": "ANSIClaw",
    "ice_colors": False
})
print("Canvas created")

# ═══════════════════════════════════════════════
# BACKGROUND — sky with texture variation
# ═══════════════════════════════════════════════

# Sky — clean gradient bands (ANSI style — banding is natural and expected)
rect(0,  0, 80, 4, F4, DBLUE, BLACK)   # deep sky top
rect(0,  4, 80, 4, F3, DBLUE, BLACK)   # mid-dark
rect(0,  8, 80, 5, F2, DBLUE, BLACK)   # mid-light
rect(0, 13, 80, 4, F1, DBLUE, BLACK)   # near-horizon, lightest

# Horizon line
rect(0, 17, 80, 1, UH, BROWN, BLACK)

# Ground — clean banded shading
rect(0, 18, 80, 2, F2, BROWN, BLACK)
rect(0, 20, 80, 2, F3, BROWN, BLACK)
rect(0, 22, 80, 1, F4, BROWN, BLACK)
rect(0, 23, 80, 1, F4, DGRAY, BLACK)
rect(0, 24, 80, 1, F4, BLACK,  BLACK)

print("Background done")

# ═══════════════════════════════════════════════
# STEM & LEAVES
# ═══════════════════════════════════════════════

cx = 39  # center x (stem = cx, cx+1)

# Stem
rect(cx,   14, 2, 1, F2, GREEN,  BLACK)   # top — lighter
rect(cx,   15, 2, 1, F3, DGREEN, BLACK)
rect(cx,   16, 2, 1, F4, DGREEN, BLACK)
rect(cx,   17, 2, 1, F3, DGREEN, BLACK)   # into ground

# Left leaf — bigger, drooping
at(cx-1, 13, LH,  GREEN,  BLACK)
at(cx-2, 13, LH,  GREEN,  BLACK)
at(cx-3, 14, LH,  GREEN,  BLACK)
at(cx-4, 14, LH,  DGREEN, BLACK)
at(cx-5, 14, LH,  DGREEN, BLACK)
at(cx-1, 14, LFH, DGREEN, BLACK)   # connect to stem
at(cx-2, 14, F3,  DGREEN, BLACK)
# leaf highlight
at(cx-2, 13, UH,  GREEN, BLACK)
at(cx-3, 13, UH,  GREEN, BLACK)

# Right leaf
at(cx+2, 15, RFH, DGREEN, BLACK)   # connect to stem
at(cx+3, 15, F3,  DGREEN, BLACK)
at(cx+4, 15, LH,  GREEN,  BLACK)
at(cx+5, 15, LH,  GREEN,  BLACK)
at(cx+6, 15, LH,  DGREEN, BLACK)
at(cx+3, 14, UH,  GREEN, BLACK)
at(cx+4, 14, UH,  GREEN, BLACK)

print("Stem & leaves done")

# ═══════════════════════════════════════════════
# PETALS  (center: cx..cx+1, rows 10..11)
# ═══════════════════════════════════════════════

# --- TOP PETAL (rows 4-9) — taller ---
at(cx,   4, UH, LMAG, BLACK)
at(cx+1, 4, UH, LMAG, BLACK)

at(cx-1, 5, LFH, LMAG, BLACK)
at(cx,   5, F1,  LMAG, BLACK)
at(cx+1, 5, F1,  LMAG, BLACK)
at(cx+2, 5, RFH, LMAG, BLACK)

at(cx-1, 6, LFH, DMAG, BLACK)
at(cx,   6, F2,  LMAG, BLACK)
at(cx+1, 6, F2,  LMAG, BLACK)
at(cx+2, 6, RFH, DMAG, BLACK)

at(cx-1, 7, LFH, DMAG, BLACK)
at(cx,   7, F3,  DMAG, BLACK)
at(cx+1, 7, F3,  DMAG, BLACK)
at(cx+2, 7, RFH, DMAG, BLACK)

at(cx-1, 8, LFH, DMAG, BLACK)
at(cx,   8, F4,  DMAG, BLACK)
at(cx+1, 8, F4,  DMAG, BLACK)
at(cx+2, 8, RFH, DMAG, BLACK)

# row 9 — bottom separator of top petal
at(cx-1, 9, LH, DMAG, BLACK)
at(cx,   9, LH, DMAG, BLACK)
at(cx+1, 9, LH, DMAG, BLACK)
at(cx+2, 9, LH, DMAG, BLACK)

# --- BOTTOM PETAL (rows 12-16) ---
at(cx-1, 12, UH, DMAG, BLACK)
at(cx,   12, UH, DMAG, BLACK)
at(cx+1, 12, UH, DMAG, BLACK)
at(cx+2, 12, UH, DMAG, BLACK)

at(cx-1, 13, LFH, DMAG, BLACK)
at(cx,   13, F4,  DMAG, BLACK)
at(cx+1, 13, F4,  DMAG, BLACK)
at(cx+2, 13, RFH, DMAG, BLACK)

at(cx-1, 14, LFH, DMAG, BLACK)
at(cx,   14, F3,  DMAG, BLACK)
at(cx+1, 14, F3,  DMAG, BLACK)
at(cx+2, 14, RFH, DMAG, BLACK)

at(cx-1, 15, LFH, LMAG, BLACK)
at(cx,   15, F2,  LMAG, BLACK)
at(cx+1, 15, F2,  LMAG, BLACK)
at(cx+2, 15, RFH, LMAG, BLACK)

at(cx,   16, F1,  LMAG, BLACK)
at(cx+1, 16, F1,  LMAG, BLACK)
at(cx-1, 16, UH, LMAG, BLACK)
at(cx+2, 16, UH, LMAG, BLACK)

# --- LEFT PETAL (wider — cols cx-8 to cx-2) ---
# Two rows: 10 and 11
for row in [10, 11]:
    at(cx-1, row, LFH, DMAG, BLACK)    # inner separator
    at(cx-2, row, F4,  DMAG, BLACK)
    at(cx-3, row, F3,  DMAG, BLACK)
    at(cx-4, row, F3,  DMAG, BLACK)
    at(cx-5, row, F2,  LMAG, BLACK)
    at(cx-6, row, F1,  LMAG, BLACK)
    at(cx-7, row, RFH, LMAG, BLACK)    # outer edge

# taper top & bottom
for col in [cx-2, cx-3, cx-4, cx-5, cx-6]:
    at(col, 9,  UH, LMAG, BLACK)
    at(col, 12, LH, LMAG, BLACK)
at(cx-7, 9,  UH, LMAG, BLACK)
at(cx-7, 12, LH, LMAG, BLACK)

# --- RIGHT PETAL (wider — cols cx+2 to cx+8) ---
for row in [10, 11]:
    at(cx+2, row, RFH, DMAG, BLACK)    # inner separator
    at(cx+3, row, F4,  DMAG, BLACK)
    at(cx+4, row, F3,  DMAG, BLACK)
    at(cx+5, row, F3,  DMAG, BLACK)
    at(cx+6, row, F2,  LMAG, BLACK)
    at(cx+7, row, F1,  LMAG, BLACK)
    at(cx+8, row, LFH, LMAG, BLACK)    # outer edge

for col in [cx+3, cx+4, cx+5, cx+6, cx+7]:
    at(col, 9,  UH, LMAG, BLACK)
    at(col, 12, LH, LMAG, BLACK)
at(cx+8, 9,  UH, LMAG, BLACK)
at(cx+8, 12, LH, LMAG, BLACK)

# --- TOP-LEFT DIAGONAL PETAL ---
# spans rows 6-9, cols cx-6..cx-2
at(cx-3, 6, UH, LMAG, BLACK)
at(cx-4, 6, UH, LMAG, BLACK)
at(cx-5, 6, UH, LMAG, BLACK)

at(cx-2, 7, LFH, LMAG, BLACK)
at(cx-3, 7, F2,  LMAG, BLACK)
at(cx-4, 7, F2,  LMAG, BLACK)
at(cx-5, 7, RFH, LMAG, BLACK)

at(cx-2, 8, LFH, DMAG, BLACK)
at(cx-3, 8, F3,  DMAG, BLACK)
at(cx-4, 8, F3,  DMAG, BLACK)
at(cx-5, 8, RFH, DMAG, BLACK)

# bottom edge of TL petal (connects into left petal row)
at(cx-3, 9, LH, DMAG, BLACK)
at(cx-4, 9, LH, DMAG, BLACK)
at(cx-5, 9, LH, LMAG, BLACK)
at(cx-6, 9, LH, LMAG, BLACK)

# --- TOP-RIGHT DIAGONAL PETAL ---
at(cx+4, 6, UH, LMAG, BLACK)
at(cx+5, 6, UH, LMAG, BLACK)
at(cx+6, 6, UH, LMAG, BLACK)

at(cx+3, 7, RFH, LMAG, BLACK)
at(cx+4, 7, F2,  LMAG, BLACK)
at(cx+5, 7, F2,  LMAG, BLACK)
at(cx+6, 7, LFH, LMAG, BLACK)

at(cx+3, 8, RFH, DMAG, BLACK)
at(cx+4, 8, F3,  DMAG, BLACK)
at(cx+5, 8, F3,  DMAG, BLACK)
at(cx+6, 8, LFH, DMAG, BLACK)

at(cx+4, 9, LH, DMAG, BLACK)
at(cx+5, 9, LH, DMAG, BLACK)
at(cx+6, 9, LH, LMAG, BLACK)
at(cx+7, 9, LH, LMAG, BLACK)

# --- BOTTOM-LEFT DIAGONAL PETAL ---
at(cx-3, 12, UH, DMAG, BLACK)
at(cx-4, 12, UH, DMAG, BLACK)
at(cx-5, 12, UH, LMAG, BLACK)
at(cx-6, 12, UH, LMAG, BLACK)

at(cx-2, 13, LFH, DMAG, BLACK)
at(cx-3, 13, F3,  DMAG, BLACK)
at(cx-4, 13, F3,  DMAG, BLACK)
at(cx-5, 13, RFH, DMAG, BLACK)

at(cx-2, 14, LFH, LMAG, BLACK)
at(cx-3, 14, F2,  LMAG, BLACK)
at(cx-4, 14, F2,  LMAG, BLACK)
at(cx-5, 14, RFH, LMAG, BLACK)

at(cx-3, 15, LH, LMAG, BLACK)
at(cx-4, 15, LH, LMAG, BLACK)
at(cx-5, 15, LH, LMAG, BLACK)

# --- BOTTOM-RIGHT DIAGONAL PETAL ---
at(cx+4, 12, UH, DMAG, BLACK)
at(cx+5, 12, UH, DMAG, BLACK)
at(cx+6, 12, UH, LMAG, BLACK)
at(cx+7, 12, UH, LMAG, BLACK)

at(cx+3, 13, RFH, DMAG, BLACK)
at(cx+4, 13, F3,  DMAG, BLACK)
at(cx+5, 13, F3,  DMAG, BLACK)
at(cx+6, 13, LFH, DMAG, BLACK)

at(cx+3, 14, RFH, LMAG, BLACK)
at(cx+4, 14, F2,  LMAG, BLACK)
at(cx+5, 14, F2,  LMAG, BLACK)
at(cx+6, 14, LFH, LMAG, BLACK)

at(cx+4, 15, LH, LMAG, BLACK)
at(cx+5, 15, LH, LMAG, BLACK)
at(cx+6, 15, LH, LMAG, BLACK)

print("Petals done")

# ═══════════════════════════════════════════════
# FLOWER CENTER (2x2 at cx,10 — yellow/brown)
# ═══════════════════════════════════════════════
# bg=BROWN=6, which is <8 so safe with ice_colors=False
at(cx,   10, F1, YELLOW, BROWN)   # top-left: brightest (lit)
at(cx+1, 10, F2, YELLOW, BROWN)   # top-right
at(cx,   11, F3, BROWN,  BLACK)   # bottom-left: shadow
at(cx+1, 11, F4, BROWN,  BLACK)   # bottom-right: deepest

print("Center done")

# ═══════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════
import os
out_dir = os.path.expanduser("~/Documents/ANSIClaw Output")
ans_path = f"{out_dir}/flower_v2.ans"
png_path = f"{out_dir}/flower_v2.png"

post("/api/file/save", {"path": ans_path})

r = requests.post(f"{BASE}/api/file/export/png", json={"path": png_path})
print("PNG export:", r.text[:80])
print(f"Saved: {ans_path}")
print("ALL DONE ✓")
