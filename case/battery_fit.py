# Finds where common LiPo pouch cells fit under the tilted PCB, using assembly.json from build_case.py.
# A cell must sit on the floor (optionally sunk into a floor pocket), stay under every part hanging below
# the PCB with CLEAR to spare, and avoid the pillars, corner ledges and walls.
import json, math, sys
a = json.load(open("assembly.json"))
th = math.radians(a["tilt_deg"]); yp = a["y_pivot"]; zr = a["z_rear"]
FLOOR_T, CLEAR, WALL_GAP = 1.0, 0.3, 0.5
SINK = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0      # pocket depth into the floor
CX, CY, IW, IH = 128.5, -52.5, 77.0, 115.0
x0c, x1c, y0c, y1c = CX - IW / 2 + WALL_GAP, CX + IW / 2 - WALL_GAP, CY - IH / 2 + WALL_GAP, CY + IH / 2 - WALL_GAP
posts = [(h[0], h[1]) for h in a["pcb"]["holes"]]
POST_R = 3.0 + 0.3
LEDGE = 1.6 + 0.3
def wz(y, z): return zr + (y - yp) * math.sin(th) + z * math.cos(th)
# everything hanging below the PCB, in world xy + lowest world z
low = []
for b in a["boxes"]:
    if b["min"][2] < 0:
        zb = min(wz(b["min"][1], b["min"][2]), wz(b["max"][1], b["min"][2]))
        low.append((b["min"][0], b["min"][1], b["max"][0], b["max"][1], zb, b["name"]))
def ceiling(x0, y0, x1, y1):
    # lowest thing above the cell footprint: a part bottom or the PCB underside itself
    c = min(wz(y0, 0), wz(y1, 0)); who = "PCB"
    for (bx0, by0, bx1, by1, zb, n) in low:
        if bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0 and zb < c:
            c, who = zb, n
    return c, who
def blocked(x0, y0, x1, y1):
    for (px, py) in posts:
        nx, ny = min(max(px, x0), x1), min(max(py, y0), y1)
        if math.hypot(px - nx, py - ny) < POST_R: return True
    # corner ledges hug the walls in the four corners
    for (cx, cy) in ((x0c, y0c), (x1c, y0c), (x0c, y1c), (x1c, y1c)):
        if abs(((x0 + x1) / 2) - cx) < 10 + (x1 - x0) / 2 and abs(((y0 + y1) / 2) - cy) < 10 + (y1 - y0) / 2:
            if min(abs(x0 - cx), abs(x1 - cx)) < LEDGE or min(abs(y0 - cy), abs(y1 - cy)) < LEDGE: return True
    return False
cells = [("301230", 3.0, 12, 30, 110), ("401230", 4.0, 12, 30, 150), ("302030", 3.0, 20, 30, 200),
         ("402030", 4.0, 20, 30, 250), ("302535", 3.0, 25, 35, 300), ("303040", 3.0, 30, 40, 350),
         ("402535", 4.0, 25, 35, 400), ("403040", 4.0, 30, 40, 500)]
for name, t, w, l, mah in cells:
    best = None
    for (dx, dy) in ((w, l), (l, w)):
        x = x0c
        while x + dx <= x1c:
            y = y0c
            while y + dy <= y1c:
                if not blocked(x, y, x + dx, y + dy):
                    c, who = ceiling(x, y, x + dx, y + dy)
                    margin = c - CLEAR - (FLOOR_T - SINK + t)
                    if margin >= 0 and (best is None or margin > best[0]):
                        best = (margin, x, y, dx, dy, who)
                y += 1
            x += 1
    if best:
        m, x, y, dx, dy, who = best
        print("%-7s %dx%dx%.0f ~%3dmAh  FITS  x %.0f..%.0f  y %.0f..%.0f  (%.1f mm spare under %s)" % (name, l, w, t, mah, x, x + dx, y, y + dy, m, who))
    else:
        print("%-7s %dx%dx%.0f ~%3dmAh  no room" % (name, l, w, t, mah))
