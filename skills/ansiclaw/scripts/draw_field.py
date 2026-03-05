#!/usr/bin/env python3
"""
Field scene: sky gradient, sun, clouds, tree with shading, grass, flowers, distant hills
Sun is upper-right => right/top of tree canopy is lit, left/bottom is shadowed
"""
import requests, os

BASE = "http://127.0.0.1:7777"

def post(path, data):
    r = requests.post(f"{BASE}{path}", json=data)
    resp = r.json()
    if not resp.get("ok"):
        print(f"  WARN {path}: {resp}")
    return resp

def rect(x, y, w, h, code=219, fg=7, bg=0):
    if w <= 0 or h <= 0: return
    post("/api/draw/rect/filled", {"x":x,"y":y,"width":w,"height":h,"code":code,"fg":fg,"bg":bg})

def at(x, y, code=219, fg=7, bg=0):
    post("/api/draw/at", {"x":x,"y":y,"code":code,"fg":fg,"bg":bg})

def line(x1,y1,x2,y2,code=219,fg=7,bg=0):
    post("/api/draw/line", {"x1":x1,"y1":y1,"x2":x2,"y2":y2,"code":code,"fg":fg,"bg":bg})

# Colors
BLACK=0; DBLUE=1; DGREEN=2; CYAN=3; RED=4; MAG=5; BROWN=6; LGRAY=7
DGRAY=8; BLUE=9; GREEN=10; LCYAN=11; LRED=12; LMAG=13; YELLOW=14; WHITE=15

# CP437 half-blocks
LOWER_HALF = 220   # ▄  fg=top color? no: fg=lower half color, bg=upper half color
UPPER_HALF = 223   # ▀  fg=upper half color, bg=lower half color

print("New canvas...")
post("/api/file/new", {"columns":80,"rows":25,"title":"Field","author":"Clawd","group":"ANSIClaw"})

# ============================================================
# SKY - gradient: deep navy at top → bright blue → pale at horizon
# ============================================================
print("Sky...")
rect(0,  0, 80, 3, 219, DBLUE,  DBLUE)   # deep navy top
rect(0,  3, 80, 3, 177, BLUE,   DBLUE)   # medium blue
rect(0,  6, 80, 3, 176, BLUE,   DBLUE)   # lighter blue
rect(0,  9, 80, 3, 176, LGRAY,  BLUE)    # pale near horizon
rect(0, 12, 80, 1, 176, WHITE,  BLUE)    # almost white at horizon line

# ============================================================
# SUN - upper right, warm with glow rings
# ============================================================
print("Sun...")
# Outer glow (sparse dots on sky)
rect(65, 0, 12, 1, 176, YELLOW, DBLUE)
rect(63, 1, 2,  5, 176, YELLOW, DBLUE)
rect(77, 1, 2,  5, 176, YELLOW, DBLUE)
rect(65, 6, 12, 1, 176, YELLOW, BLUE)
# Mid glow ring
rect(65, 1, 12, 5, 177, YELLOW, BLUE)
# Core - solid bright yellow
rect(67, 1, 8,  4, 219, YELLOW, YELLOW)
# Warm spot highlight
rect(68, 1, 5,  2, 219, WHITE,  YELLOW)

# ============================================================
# CLOUDS
# ============================================================
print("Clouds...")
# Cloud 1 - left
rect(4,  2, 13, 1, 219, WHITE, WHITE)
rect(3,  3, 15, 2, 219, WHITE, WHITE)
rect(5,  5,  9, 1, 219, WHITE, WHITE)
rect(3,  5, 15, 1, 177, LGRAY, BLUE)   # shadow underside

# Cloud 2 - centre-left
rect(27, 1, 8,  1, 219, WHITE, WHITE)
rect(25, 2, 12, 2, 219, WHITE, WHITE)
rect(26, 4, 10, 1, 177, LGRAY, BLUE)   # shadow underside

# ============================================================
# HORIZON LINE
# ============================================================
# ▄ lower-half green on blue sky = crisp horizon
rect(0, 12, 80, 1, LOWER_HALF, GREEN, BLUE)

# ============================================================
# GROUND - layered shading, bright near horizon, darkens down
# ============================================================
print("Ground...")
rect(0, 13, 80, 2, 176, GREEN,  DGREEN)   # bright lit top (sunlit)
rect(0, 15, 80, 3, 177, GREEN,  DGREEN)   # mid green
rect(0, 18, 80, 3, 219, DGREEN, DGREEN)   # solid mid-dark
rect(0, 21, 80, 4, 178, DGREEN, BLACK)    # dark bottom, dense grass

# Grass texture hints (random bright blades near top of ground)
for x in [2,7,11,16,20,43,47,53,58,62,67,72,76]:
    at(x, 13, 124, GREEN, DGREEN)   # | pipe = grass blade

# ============================================================
# DISTANT TREELINE / HILLS on the horizon (right background)
# ============================================================
print("Distant hills...")
# Rolling hill silhouette - bump shapes using ▀ upper-half blocks
# fg = dark green (hill), bg = pale sky blue
hill = [(48,2),(49,3),(50,3),(51,3),(52,4),(53,4),(54,4),(55,4),(56,3),(57,3),
        (58,3),(59,2),(60,2),(61,2),(62,3),(63,3),(64,3),(65,3),(66,2),(67,1),
        (68,2),(69,2),(70,2),(71,2),(72,1),(73,1),(74,2),(75,2),(76,2),(77,3),
        (78,3),(79,3)]

for (x, depth) in hill:
    # paint a vertical strip from row (12-depth) to row 12 with dark green
    rect(x, 12-depth, 1, depth, 219, DGREEN, DGREEN)
# Soften top edge with half-blocks
for (x, depth) in hill:
    at(x, 12-depth-1, LOWER_HALF, DGREEN, BLUE)

# ============================================================
# TREE
# Sun is upper-right → lit = top + right side of canopy
# Shadow = left + bottom of canopy
# Tree centred ~col 28, canopy rows 4-17, trunk rows 17-24
# ============================================================
print("Tree...")

# --- Shadow cast on ground (stretches left, away from upper-right sun) ---
rect(8,  18, 22, 1, 178, BLACK,  DGREEN)
rect(10, 19, 18, 1, 178, BLACK,  DGREEN)
rect(13, 20, 14, 1, 178, DGRAY,  DGREEN)
rect(16, 21, 10, 1, 178, DGRAY,  DGREEN)

# --- Trunk ---
# Right edge bright (lit), left edge dark
rect(27, 17, 3, 8, 219, BROWN, BLACK)
rect(27, 17, 1, 8, 219, DGRAY, BLACK)   # shadow left edge
rect(29, 17, 1, 8, 219, YELLOW, BROWN)  # highlight right edge (lit)

# Roots at base
at(26, 24, 92, BROWN, BLACK)   # └
at(30, 24, 217, BROWN, BLACK)  # ┘ (CP437 code 217)

# --- Canopy layers (painted dark → mid → light, building up) ---

# Layer 1: dark shadow base (left & bottom) - dark green on black
rect(15, 12, 16, 6, 219, DGREEN, BLACK)
rect(15,  9, 10, 5, 219, DGREEN, BLACK)

# Layer 2: main canopy mass - medium dark green
rect(14, 11, 22, 7, 219, DGREEN, DGREEN)
rect(17,  8, 18, 5, 219, DGREEN, DGREEN)
rect(20,  6, 14, 4, 219, DGREEN, DGREEN)

# Layer 3: mid-lit (right/upper portion) - bright green
rect(24,  8, 14, 6, 219, GREEN, DGREEN)
rect(22,  6, 12, 4, 219, GREEN, DGREEN)
rect(25,  5,  9, 3, 219, GREEN, DGREEN)

# Layer 4: brightest highlight (top-right, faces sun directly)
rect(29,  4, 10, 5, 219, GREEN, GREEN)   # fully lit
rect(33,  8,  5, 4, 219, GREEN, GREEN)

# Layer 5: specular highlight tip
rect(30,  4,  7, 2, 219, YELLOW, GREEN)  # yellow-green sun kiss on crown

# --- Canopy edge softening with half-blocks ---
# Top edge: ▀ with green fg on sky bg
rect(20, 4, 14, 1, UPPER_HALF, GREEN, BLUE)    # top of canopy
rect(30, 3,  7, 1, UPPER_HALF, YELLOW, BLUE)   # highest tip
# Left edge: darker side
rect(14, 11, 1, 6, LOWER_HALF, DGREEN, BLACK)
# Bottom edge of canopy blending into ground
rect(15, 17, 22, 1, UPPER_HALF, DGREEN, DGREEN)

# Leaf detail - little bumps on the lit side
for (x,y) in [(33,6),(35,7),(36,5),(38,9),(37,11)]:
    at(x, y, 6, GREEN, GREEN)  # ♠ spade as leaf cluster

# ============================================================
# WILDFLOWERS in the foreground grass
# ============================================================
print("Flowers...")
flowers = [
    (3,20,RED),(6,22,YELLOW),(9,21,WHITE),(12,23,LMAG),(50,20,RED),
    (54,22,YELLOW),(57,21,WHITE),(61,23,LMAG),(64,20,RED),(68,22,YELLOW),
    (72,20,WHITE),(75,21,LMAG),(45,23,RED),(48,21,YELLOW),(2,23,WHITE),
]
for (fx,fy,fc) in flowers:
    at(fx, fy, 5, fc, DGREEN)    # ♣ as flower on dark grass
    at(fx, fy-1, 124, GREEN, DGREEN)  # | stem

# ============================================================
# EXPORT
# ============================================================
print("Exporting...")
post("/api/file/save-as",   {"path": os.path.expanduser("~/Desktop/field.ans")})
post("/api/file/export/png",{"path": os.path.expanduser("~/Desktop/field.png")})
print("✅ Done! ~/Desktop/field.png + field.ans")
