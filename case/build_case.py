# Generates the case from the board (single source of truth for the stack-up):
#   case_bottom.jscad  tilted tray: flat floor, PCB parallel to the sloped top edge,
#                      screw pillars + corner support ledges cut to the PCB underside,
#                      rear-wall windows for USB-C / reset / power.
#   case_plate.jscad   switch plate (board frame, plate top up), inset inside the tray walls,
#                      with Gateron LP stabilizer cutouts, spacer bosses and an edge rim underneath.
#   assembly.json      PCB + part boxes for viewer.html and the collision report below.
# Run with KiCad's python:  "C:/Program Files/KiCad/8.0/bin/python.exe" build_case.py
# then render each .jscad with @jscad/cli@1 (see CLAUDE.md).
#
# Frames: "board frame" = ergogen xy (x = kicad_x, y = -kicad_y), z = 0 at the PCB underside,
# PCB flat. "world" = case frame, z = 0 under the floor. World = board frame rotated about the
# x axis by TILT_DEG around the PCB's rear edge (y = Y_PIVOT), then lifted by Z_REAR.
import json, math, os, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "..", "output", "pcbs", "not_about_money.kicad_pcb")

# ---- case ----
FLOOR_T = 1.0
TILT_DEG = 2.37            # rear higher
FLOOR_CLEAR = 0.5          # min gap between the lowest part and the floor
WALL_T = 1.2
PCB_TOL = 0.25             # PCB edge to wall, per side
POST_R, SCREW_R = 3.0, 1.1
# M2 countersunk (bevel-head) screws go in from the top: countersink in the plate, clearance through
# the plate boss and PCB, then self-tap into a blind pilot in the pillar. Every hole runs square to the
# tilted board, so the head sits flush in the plate, and nothing shows under the case.
CSK_R = 2.0                # countersink top radius (M2 DIN 965 head dk 3.8), 90 deg
PILOT_R = 0.8              # self-tapping M2 pilot in the pillar; runs the full pillar, stops flat on the floor
PILOT_EXTRA = 0.5          # min pilot left below the screw tip
MIN_THREAD = 1.5
SCREW_LENGTHS = [4, 5, 6, 8, 10, 12]   # countersunk length includes the head
LEDGE_W, LEDGE_ARM = 1.6, 10.0   # corner support ledges: width in from the wall, arm length
GAP = 0.4                  # wiggle room around each wall cutout, per side
PITCH = 19.0
KEYCAP = 18.0              # 1u keycap; 2u = 2 * PITCH - 1

# ---- plate ----
PCB_T = 1.6
PLATE_T = 1.2              # Gateron LP stabilizers are specced for a 1.2 plate
PLATE_TOP = PCB_T + 2.2    # plate top above the PCB underside (Gateron LP: 2.2 above PCB top)
PLATE_TOL = 0.2            # plate edge to tray wall, per side
SW_CUT = 14.0              # switch cutout
PIN_RELIEF = 0.5           # clearance around THT pins poking up through the PCB
PLATE_SKIN = 0.6           # pin reliefs are blind pockets from below; this much plate stays on top
SPACER_R = 2.15            # spacer bosses around the screw holes (M2 spacer size)
RIM_W = 1.2                # support rim along the plate edge, underneath
# Gateron LP plate-mount stabilizer KS-57B210T: housings 24.00 apart, plate cutout 6.00 x 12.50
# with a 1.70 notch, joined to the switch hole by a neck (Gateron "suggested mounting" drawing).
STAB_DX, STAB_W, STAB_H = 12.0, 6.0, 12.5
STAB_NOTCH_W, STAB_NOTCH_D, STAB_NECK_H = 1.7, 1.0, 2.0
# From the KS-57B210T STEP, in a stem-centred frame with the bar on the -y side:
STAB_CUT_Y = -0.25           # plate cutout spans y -6.5..+6.0 (clip hooks under the plate at -6.5);
                             # the notch is on the +y end, away from the bar
STAB_HOUSING = (2.93, -9.70, 5.13, 4.45)   # below the plate: half-width, y range, depth below plate top
STAB_FLANGE = (3.0, -7.90, 7.23, 1.2)      # on top of the plate
STAB_BAR = (-7.975, 0.5, 0.725)            # bar y, radius, centre depth below the plate underside

# ---- part heights below the PCB (board frame, positive = depth below the underside) ----
SOCKET_H = 1.85            # Gateron LP HS 2.0 socket (KS-2P02B01-02)
SOCKET_TAB_H = 0.4         # its solder tabs (+ solder)
# Official Gateron LP socket footprint (KS-2P02B01-02, "Gateron_Low_Profile_Socket" from the user), local
# KiCad coords of an unrotated switch: body outline from its B.SilkS, solder tabs from its B.Fab rects.
SOCKET_BODY = [(-7.0, 2.53, -3.0, 6.87), (-3.0, 3.0, -1.5, 7.4), (-1.5, 3.58, 5.2, 7.92)]
SOCKET_TABS = [(-9.55, 3.425, -7.0, 5.975), (5.2, 4.475, 7.75, 7.025)]
# On the 2u keys the pad-1 tab reaches into the stabilizer cutout/housing. The user sands it down by hand:
# 1.1mm off the tip leaves 1.45 of tab, ending 0.3 inside the cutout edge (and clear of the housing).
SOCKET_TAB0_TRIM_2U = 1.1
# Battery: 301230 LiPo pouch (3.0 x 12 x 30, ~110mAh, nice!nano's recommended cell, with protection
# board + JST PH lead). It sits in a floor pocket at the best-clearance spot found under the PCB.
BATTERY = (3.0, 12.0, 30.0)      # thickness, width, length
BATT_POCKET_D = 0.5              # pocket depth into the 1.0 floor
BATT_GAP = 0.5                   # pocket clearance around the cell, per side
BATT_CLEAR = 0.3                 # min space between the cell top and anything above it
BATT_WIRE = (4.0, 6.0)           # lead notch at the end facing the JST: width, length
DIODE_H = 1.15             # SOD-123
# Panasonic EVQ-PU (PUA02K / PUC02K) datasheet: 4.7 x 3.5 body, height 1.65 +0.3/-0.1 (modelled at the max),
# 2.6-wide push plate sticking out 1.0, 0.3 travel. Plunger depth range is centred on the body.
RST_H, RST_PLUNGER = 1.95, (0.35, 1.35)
# MSK-12C02-style side slide switch, H = 2.5 variant (same land pattern as the Alps SSSS811101):
# 6.65 x 2.7 x 1.4 body; actuator 1.3 wide, 1.1 thick (centred 0.65 off the board), sticks out 2.5
# from the body face, 1.5 travel -> 2.8 total sweep. The lever pokes ~0.55 past the outer rear wall.
PWR_H, PWR_LEVER, PWR_LEVER_W, PWR_TRAVEL, PWR_LEVER_OUT = 1.4, (0.1, 1.2), 1.3, 1.5, 2.5
PWR_BODY = (6.65, 2.7)
# JST PH S2B-PH-K-S datasheet: 5.9 wide, 7.6 deep, 4.8 tall; the mated PHR-2 plug (5.8 wide, 4.5 tall)
# reaches 9.6 from the back of the header; allow 3 more for the wires to bend away
JST_H, JST_PLUG = 4.8, (9.6, 3.0, 5.8, 4.5)
# nice!nano v2 from its CAD model ("nice!nano v2.step", GCT USB4520-03-0-A mid-mount USB-C). Mounted
# components-away (reverse_mount: false), so the bare face is toward our PCB, HEADER_GAP below it
# (2.5 plastic header spacers). PCB 17.8 x 33.2 x 1.4; parts up to 1.1 above its outer face.
# USB-C shell 8.94 x 3.16, from 0.783 *above* the bare face (toward our PCB) to 1.977 past the outer
# face; mouth 4.747 past the first header pin row, 6.5 deep, centred on the board width (+-0.075).
HEADER_GAP, NANO_T, NANO_PARTS_H = 2.5, 1.4, 1.1
NANO_W, NANO_L, NANO_EDGE = 17.8, 33.2, 3.79     # NANO_EDGE: first pin row to the USB-end board edge
USB_W, USB_H, USB_D, USB_OUT, USB_INTO_GAP = 8.94, 3.16, 6.5, 4.747, 0.783
# Preview offset: slides the nano toward the top edge (KiCad -y) in the case model only, to try a move
# before changing the PCB. Keep it 0 when the board is current (the 1.5 move is now in config.yaml).
NANO_SHIFT = 0.0
USB_GAP = 0.25             # USB-C window clearance per side (from the CAD model; other windows use GAP)
# cable-head scoop around the USB-C window: w x h, corner radius. The USB mouth sits 0.8 inside the inner
# wall face, so a collar inside the case fills in around the port: the scoop is a recess from the outer
# face down to a back wall flush with the USB mouth, and only the USB window goes through that.
USB_SCOOP = (12.5, 6.5, 1.5)
COLLAR_M = 1.2             # collar margin around the scoop (sides and below; it runs down to the floor)
COLLAR_T = 0.6             # collar thickness behind the mouth plane (clear of the nano's PCB edge)
COLLAR_TOP = 0.2           # collar top stays this far below the PCB underside
LED_H = 1.1                # 0603 status LED on the PCB *top*: allow any 0603 (thin LTST-C191 is 0.55)
LED_POCKET = (3.8, 2.0)    # counterbore in the plate underside over the LED + its pads (blind, PLATE_SKIN left)
LED_HOLE_R = 0.9           # light hole through the plate above it, under the keycap-gap crossing
R0603_H = 0.45             # 0603 resistor on the back

mm = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
ol = ps.Outline(0)
outline = [[mm(ol.CPoint(i).x), -mm(ol.CPoint(i).y)] for i in range(ol.PointCount())]
poly_holes = [[[mm(h.CPoint(i).x), -mm(h.CPoint(i).y)] for i in range(h.PointCount())]
              for h in (ps.Hole(0, k) for k in range(ps.HoleCount(0)))]
px0, px1 = min(p[0] for p in outline), max(p[0] for p in outline)
py0, py1 = min(p[1] for p in outline), max(p[1] for p in outline)
CX, CY = (px0 + px1) / 2, (py0 + py1) / 2
PCB_R = 0.25               # board corner radius (= board_expand)
INNER = (px1 - px0 + 2 * PCB_TOL, py1 - py0 + 2 * PCB_TOL, PCB_R + PCB_TOL)
OUTER = (INNER[0] + 2 * WALL_T, INNER[1] + 2 * WALL_T, INNER[2] + WALL_T)
Y_PIVOT = py1                         # PCB rear edge
Y_REAR_IN = CY + INNER[1] / 2
Y_REAR_OUT = CY + OUTER[1] / 2
POSTS = [[mm(f.GetPosition().x), -mm(f.GetPosition().y)]
         for f in b.GetFootprints() if "mounting_hole" in f.GetFPIDAsString()]

boxes, reliefs = [], []
def box(name, kind, kx0, ky0, kx1, ky1, d0, d1):
    """KiCad xy extents + depth range below the PCB underside (negative = above)."""
    boxes.append({"name": name, "kind": kind,
                  "min": [min(kx0, kx1), -max(ky0, ky1), -max(d0, d1)],
                  "max": [max(kx0, kx1), -min(ky0, ky1), -min(d0, d1)]})

def pads(f, pred):
    r = [1e9, 1e9, -1e9, -1e9]
    for p in f.Pads():
        if pred(p):
            bb = p.GetBoundingBox()
            r = [min(r[0], mm(bb.GetLeft())), min(r[1], mm(bb.GetTop())),
                 max(r[2], mm(bb.GetRight())), max(r[3], mm(bb.GetBottom()))]
    return r
smd = lambda p: p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
pth = lambda p: p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH

switches, stabs, cut, lights = [], [], {}, []
sw_xy = [(mm(f.GetPosition().x), mm(f.GetPosition().y)) for f in b.GetFootprints()
         if "switch_gateron" in f.GetFPIDAsString()]
grid_x = sorted(set(round(x, 2) for x, _ in sw_xy if sum(abs(x - x2) < 0.01 for x2, _ in sw_xy) > 1))
grid_y = sorted(set(round(y, 2) for _, y in sw_xy if sum(abs(y - y2) < 0.01 for _, y2 in sw_xy) > 1))
on = lambda v, g: any(abs(v - q) < 0.01 for q in g)

for f in b.GetFootprints():
    ref, fid = f.GetReference(), f.GetFPIDAsString()
    x, y = mm(f.GetPosition().x), mm(f.GetPosition().y)
    top = -PCB_T
    if "switch_gateron" in fid:
        switches.append([x, -y])
        # Gateron KS-33 (spec KS-33E10B055NN-Y24): 14.0 body through the plate, 14.7 flange on the
        # plate top, 13.75 upper housing, 5.75 from the PCB top to the stem top
        pt = top - (PLATE_TOP - PCB_T)            # plate top, as a depth
        box(ref, "switch", x - 7.0, y - 7.0, x + 7.0, y + 7.0, top, pt)
        box(ref + "_flange", "switch", x - 7.35, y - 7.35, x + 7.35, y + 7.35, pt, pt - 1.0)
        box(ref + "_top", "switch", x - 6.875, y - 6.875, x + 6.875, y + 6.875, pt - 1.0, top - 4.55)
        box(ref + "_stem", "stem", x - 2.0, y - 0.55, x + 2.0, y + 0.55, top - 4.55, top - 5.75)
        box(ref + "_stem2", "stem", x - 0.55, y - 2.0, x + 0.55, y + 2.0, top - 4.55, top - 5.75)
        # hotswap socket from the official footprint, rotated with the switch (KiCad: +deg = CCW on screen)
        o = math.radians(f.GetOrientationDegrees()); co, so = math.cos(o), math.sin(o)
        def xf(r):
            pts = [(x + lx * co + ly * so, y - lx * so + ly * co) for lx in (r[0], r[2]) for ly in (r[1], r[3])]
            return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)
        for i, r in enumerate(SOCKET_BODY):
            box("%s_socket%d" % (ref, i), "socket", *xf(r), 0, SOCKET_H)
        # 2u keys sit between grid lines: horizontal if off-grid in x, vertical if off-grid in y
        rot = 0 if not on(x, grid_x) else (90 if not on(y, grid_y) else None)
        for i, r in enumerate(SOCKET_TABS):
            if i == 0 and rot is not None:
                r = (r[0] + SOCKET_TAB0_TRIM_2U, r[1], r[2], r[3])
            box("%s_tab%d" % (ref, i), "sockettab", *xf(r), 0, SOCKET_TAB_H)
        kw = KEYCAP + (PITCH if rot == 0 else 0); kh = KEYCAP + (PITCH if rot == 90 else 0)
        box(ref + "_cap", "keycap", x - kw / 2, y - kh / 2, x + kw / 2, y + kh / 2, top - 5.0, top - 8.0)
        if rot is not None:
            # bar points inward, toward the board centre (the PCB slot for it is cut that way)
            ex, ey = x, -y                                           # ergogen frame
            dvec = (0.0, math.copysign(1, CY - ey)) if rot == 0 else (math.copysign(1, CX - ex), 0.0)
            vvec = (1.0, 0.0) if rot == 0 else (0.0, 1.0)            # along the bar
            stabs.append([ex, ey, math.degrees(math.atan2(dvec[1], dvec[0])) + 90])   # local -y -> dvec
            def sbox(name, kind, a0, a1, ly0, ly1, z0, z1):
                # local: a along the bar, ly with the bar at -y; z in the board frame
                pts = [(ex + a * vvec[0] - l * dvec[0], ey + a * vvec[1] - l * dvec[1]) for a in (a0, a1) for l in (ly0, ly1)]
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                box(name, kind, min(xs), -max(ys), max(xs), -min(ys), -z1, -z0)
            hw, hy0, hy1, hd = STAB_HOUSING
            fw, fy0, fy1, ft = STAB_FLANGE
            by, br, bz = STAB_BAR
            pbot = PLATE_TOP - PLATE_T
            for sgn in (-1, 1):
                c = sgn * STAB_DX
                sbox("%s_stab%d" % (ref, sgn), "stab", c - hw, c + hw, hy0, hy1, PLATE_TOP - hd, pbot)
                sbox("%s_stabf%d" % (ref, sgn), "stab", c - fw, c + fw, fy0, fy1, PLATE_TOP, PLATE_TOP + ft)
            sbox(ref + "_stabbar", "stab", -STAB_DX, STAB_DX, by - br, by + br, pbot - bz - br, pbot - bz + br)
        continue
    if "mounting_hole" in fid:
        continue
    # THT pins of side-B parts poke up through the PCB: relieve them in the plate
    dy = NANO_SHIFT if "mcu_nice_nano" in fid else 0.0       # preview shift (ergogen +y = toward the top edge)
    for p in f.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            bb = p.GetBoundingBox()
            reliefs.append([mm(bb.GetLeft()) - PIN_RELIEF, -mm(bb.GetBottom()) - PIN_RELIEF + dy,
                            mm(bb.GetRight()) + PIN_RELIEF, -mm(bb.GetTop()) + PIN_RELIEF + dy])
    if "diode" in fid:
        s = pads(f, smd)
        cx, cy = (s[0] + s[2]) / 2, (s[1] + s[3]) / 2
        hx, hy = (1.35, 0.8) if (s[2] - s[0]) > (s[3] - s[1]) else (0.8, 1.35)
        box(ref, "diode", cx - hx, cy - hy, cx + hx, cy + hy, 0, DIODE_H)
    elif "mcu_nice_nano" in fid:
        n0 = HEADER_GAP; n1 = n0 + NANO_T             # nano PCB depth range
        y -= NANO_SHIFT
        pin1_y = y - 12.7                             # header row nearest the USB end
        top_y = pin1_y - NANO_EDGE
        box("nano", "nano", x - NANO_W / 2, top_y, x + NANO_W / 2, top_y + NANO_L, n0, n1)
        box("nano_parts", "nano_parts", x - 6.5, top_y + 6.0, x + 6.5, top_y + 26.0, n1, n1 + NANO_PARTS_H)
        usb_cx = x
        mouth = pin1_y - USB_OUT
        u0 = n0 - USB_INTO_GAP
        box("usb_c", "usb", usb_cx - USB_W / 2, mouth, usb_cx + USB_W / 2, mouth + USB_D, u0, u0 + USB_H)
        cut["usb"] = (usb_cx, u0 + USB_H / 2, USB_W, USB_H)
        for p in f.Pads():
            if pth(p):
                hx, hy = mm(p.GetPosition().x), mm(p.GetPosition().y) - NANO_SHIFT
                box("hdr", "header", hx - 1.25, hy - 1.25, hx + 1.25, hy + 1.25, 0, HEADER_GAP)
    elif "smd_0603" in fid and ref.startswith("LED"):
        box(ref, "led", x - 0.8, y - 0.4, x + 0.8, y + 0.4, top, top - LED_H)
        lights.append([x, -y])
        lw, lh = LED_POCKET if abs(f.GetOrientationDegrees()) % 180 < 45 else LED_POCKET[::-1]
        reliefs.append([x - lw / 2, -y - lh / 2, x + lw / 2, -y + lh / 2])
    elif "smd_0603" in fid:
        box(ref, "part", x - 0.8, y - 0.4, x + 0.8, y + 0.4, 0, R0603_H)
    elif "reset_switch" in fid:
        box(ref, "part", x - 2.35, y - 1.75, x + 2.35, y + 1.75, 0, RST_H)
        box(ref + "_plunger", "actuator", x - 1.3, y - 2.75, x + 1.3, y - 1.75, *RST_PLUNGER)
        cut["rst"] = (x, sum(RST_PLUNGER) / 2, 2.6, RST_PLUNGER[1] - RST_PLUNGER[0])
    elif "power_switch" in fid:
        bw, bd = PWR_BODY[0] / 2, PWR_BODY[1] / 2
        box(ref, "part", x - bw, y - bd, x + bw, y + bd, 0, PWR_H)
        # lever drawn in the "on" position; the cutout covers its full x +-1.65 travel
        lx = x + PWR_TRAVEL / 2                  # lever drawn in one end position
        box(ref + "_lever", "actuator", lx - PWR_LEVER_W / 2, y - bd - PWR_LEVER_OUT, lx + PWR_LEVER_W / 2, y - bd, *PWR_LEVER)
        cut["pwr"] = (x, sum(PWR_LEVER) / 2, PWR_LEVER_W + PWR_TRAVEL, PWR_LEVER[1] - PWR_LEVER[0])
    elif "jst" in fid:
        fab = [1e9, 1e9, -1e9, -1e9]
        for g in f.GraphicalItems():
            if g.GetLayerName() == "B.Fab":
                bb = g.GetBoundingBox()
                fab = [min(fab[0], mm(bb.GetLeft())), min(fab[1], mm(bb.GetTop())),
                       max(fab[2], mm(bb.GetRight())), max(fab[3], mm(bb.GetBottom()))]
        box(ref, "part", fab[0], fab[1], fab[2], fab[3], 0, JST_H)
        # mated plug + wire bend on the open side (+x: the pins sit at the back, -x, end)
        reach, bend, pw, ph = JST_PLUG
        jcy = (fab[1] + fab[3]) / 2
        box(ref + "_plug", "plug", fab[2], jcy - pw / 2, fab[0] + reach + bend, jcy + pw / 2, 0, ph)

# ---- tilt: lift the board until the lowest part clears the floor ----
th = math.radians(TILT_DEG)
def world_z(y, z, z_rear):
    return z_rear + (y - Y_PIVOT) * math.sin(th) + z * math.cos(th)
need = 0
for bx in boxes:
    if bx["min"][2] < 0:
        for yy in (bx["min"][1], bx["max"][1]):
            need = max(need, FLOOR_T + FLOOR_CLEAR - world_z(yy, bx["min"][2], 0))
Z_REAR = math.ceil(need * 10) / 10
print("case: inner %.2f x %.2f, outer %.2f x %.2f, centre (%.2f, %.2f)" % (INNER[0], INNER[1], OUTER[0], OUTER[1], CX, CY))
print("PCB underside: rear edge z=%.2f, front edge z=%.2f" % (Z_REAR, world_z(py0, 0, Z_REAR)))
print("plate/wall top: rear z=%.2f, front z=%.2f" % (world_z(Y_REAR_OUT, PLATE_TOP, Z_REAR),
                                                    world_z(CY - OUTER[1] / 2, PLATE_TOP, Z_REAR)))

# ---- screws: longest standard M2 countersunk per pillar; the pilot runs down to the floor top ----
screws = []
for (px, py) in POSTS:
    pillar_top = world_z(py, 0, Z_REAR)
    room = (pillar_top - FLOOR_T) / math.cos(th)                # pilot depth along the tilted axis
    fits = [l for l in SCREW_LENGTHS if MIN_THREAD <= l - PLATE_TOP <= room - PILOT_EXTRA]
    if not fits:
        raise SystemExit("no standard screw fits the pillar at (%.1f, %.1f)" % (px, py))
    L = max(fits)
    screws.append((px, py, L, round(room, 2), pillar_top))

# ---- corner ledges (board-frame rects [x0, y0, x1, y1], clipped to the cavity in jscad) ----
ix0, ix1 = CX - INNER[0] / 2, CX + INNER[0] / 2
iy0, iy1 = CY - INNER[1] / 2, CY + INNER[1] / 2
ledges = []
for (xw, sx) in ((ix0, 1), (ix1, -1)):
    for (yw, sy) in ((iy0, 1), (iy1, -1)):
        xs, ys = sorted([xw, xw + sx * LEDGE_ARM]), sorted([yw, yw + sy * LEDGE_W])
        ledges.append([xs[0], ys[0], xs[1], ys[1]])
        xs, ys = sorted([xw, xw + sx * LEDGE_W]), sorted([yw, yw + sy * LEDGE_ARM])
        ledges.append([xs[0], ys[0], xs[1], ys[1]])

# ---- plate underside supports: rim along the edge + spacer bosses ----
pw, ph, pr = INNER[0] - 2 * PLATE_TOL, INNER[1] - 2 * PLATE_TOL, INNER[2] - PLATE_TOL
plate_gap = PLATE_TOP - PLATE_T - PCB_T          # plate underside to PCB top

# ---- USB collar (board frame: y ergogen, z = 0 at the PCB underside, negative below) ----
ub = next(bx for bx in boxes if bx["name"] == "usb_c")
usb_mouth = ub["max"][1]
collar = None if usb_mouth >= Y_REAR_IN - 0.05 else [cut["usb"][0] - USB_SCOOP[0] / 2 - COLLAR_M, usb_mouth - COLLAR_T,
          cut["usb"][0] + USB_SCOOP[0] / 2 + COLLAR_M, Y_REAR_IN + 0.5, -COLLAR_TOP]

# ---- collision report ----
def overlap(bx, r):
    return bx["min"][0] < r[2] and bx["max"][0] > r[0] and bx["min"][1] < r[3] and bx["max"][1] > r[1]
def circ_hits(bx, c, rad):
    nx = min(max(c[0], bx["min"][0]), bx["max"][0]); ny = min(max(c[1], bx["min"][1]), bx["max"][1])
    return math.hypot(c[0] - nx, c[1] - ny) < rad
issues = []
rim = [[CX - pw / 2, CY - ph / 2, CX + pw / 2, CY - ph / 2 + RIM_W], [CX - pw / 2, CY + ph / 2 - RIM_W, CX + pw / 2, CY + ph / 2],
       [CX - pw / 2, CY - ph / 2, CX - pw / 2 + RIM_W, CY + ph / 2], [CX + pw / 2 - RIM_W, CY - ph / 2, CX + pw / 2, CY + ph / 2]]
for bx in boxes:
    below = bx["min"][2] < 0                       # anything reaching under the PCB
    between = bx["max"][2] > PCB_T and bx["min"][2] < PLATE_TOP - PLATE_T   # in the plate gap
    for c in POSTS:
        if below and circ_hits(bx, c, POST_R):
            issues.append("%s hits standoff %s" % (bx["name"], c))
        if between and circ_hits(bx, c, SPACER_R):
            issues.append("%s hits plate spacer %s" % (bx["name"], c))
    if collar and bx["name"] != "usb_c" and bx["min"][2] < -COLLAR_TOP and overlap(bx, collar[:4]):
        issues.append("%s hits the USB collar" % bx["name"])
    for L in ledges:
        if below and overlap(bx, L):
            issues.append("%s hits corner ledge %s" % (bx["name"], [round(v, 1) for v in L]))
    for R in rim:
        if between and overlap(bx, R) and not bx["kind"].startswith("switch"):
            issues.append("%s hits plate rim" % bx["name"])
        if between and bx["kind"] == "switch" and overlap(bx, R):
            issues.append("%s housing hits plate rim" % bx["name"])
# sockets vs stabilizer housings (both hang below the PCB), and socket parts that would sit over a PCB cutout
def inside(pt, poly):
    x, y = pt; c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
stab_boxes = [bx for bx in boxes if bx["kind"] == "stab" and bx["min"][2] < 0]
for bx in boxes:
    if not bx["kind"].startswith("socket"):
        continue
    for sb in stab_boxes:
        if overlap(bx, [sb["min"][0], sb["min"][1], sb["max"][0], sb["max"][1]]):
            issues.append("%s hits stabilizer %s" % (bx["name"], sb["name"]))
    (x0, y0, _), (x1, y1, _) = bx["min"], bx["max"]
    if any(inside((x0 + (x1 - x0) * i / 6, y0 + (y1 - y0) * j / 6), h) for i in range(7) for j in range(7) for h in poly_holes):
        issues.append("%s sits over a PCB cutout" % bx["name"])

led_room = plate_gap + PLATE_T - PLATE_SKIN      # gap + counterbore
if LED_H > led_room - 0.2:
    issues.append("LED (%.2f tall) leaves < 0.2 under the plate counterbore (room %.2f)" % (LED_H, led_room))
print("LED room under the plate: %.2f (gap %.2f + counterbore %.2f)" % (led_room, plate_gap, PLATE_T - PLATE_SKIN))

# ---- battery: best-clearance spot for the cell in a floor pocket ----
bt, bw, bl = BATTERY
low = []
for b_ in boxes:
    if b_["min"][2] < 0:
        zb = min(world_z(b_["min"][1], b_["min"][2], Z_REAR), world_z(b_["max"][1], b_["min"][2], Z_REAR))
        low.append((b_["min"][0], b_["min"][1], b_["max"][0], b_["max"][1], zb, b_["name"]))
def ceiling(x0, y0, x1, y1):
    c, who = min(world_z(y0, 0, Z_REAR), world_z(y1, 0, Z_REAR)), "PCB"
    for (a0, b0, a1, b1, zb, n) in low:
        if a0 < x1 and a1 > x0 and b0 < y1 and b1 > y0 and zb < c:
            c, who = zb, n
    return c, who
def batt_blocked(x0, y0, x1, y1):
    g = BATT_GAP
    for (px, py) in POSTS:
        nx, ny = min(max(px, x0 - g), x1 + g), min(max(py, y0 - g), y1 + g)
        if math.hypot(px - nx, py - ny) < POST_R: return True
    for L in ledges:
        if L[0] < x1 + g and L[2] > x0 - g and L[1] < y1 + g and L[3] > y0 - g: return True
    return x0 - g < ix0 + 0.3 or x1 + g > ix1 - 0.3 or y0 - g < iy0 + 0.3 or y1 + g > iy1 - 0.3
batt = None
for (dx, dy) in ((bw, bl), (bl, bw)):
    for i in range(int((ix1 - ix0) * 2)):
        for j in range(int((iy1 - iy0) * 2)):
            x0b, y0b = ix0 + i * 0.5, iy0 + j * 0.5
            if batt_blocked(x0b, y0b, x0b + dx, y0b + dy): continue
            c, who = ceiling(x0b, y0b, x0b + dx, y0b + dy)
            spare = c - (FLOOR_T - BATT_POCKET_D + bt) - BATT_CLEAR
            if spare >= 0 and (batt is None or spare > batt[0] + 1e-9):
                batt = (spare, x0b, y0b, x0b + dx, y0b + dy, who)
batt_rect, wire_rect = None, None
if batt is None:
    issues.append("battery %gx%gx%g does not fit anywhere" % (bl, bw, bt))
else:
    spare, bx0, by0, bx1, by1, who = batt
    batt_rect = [bx0, by0, bx1, by1]
    # lead notch on the short end nearest the JST connector
    jst = [b_ for b_ in boxes if b_["name"].startswith("JST") and b_["kind"] == "part"][0]
    jx, jy = (jst["min"][0] + jst["max"][0]) / 2, (jst["min"][1] + jst["max"][1]) / 2
    ww, wl = BATT_WIRE
    if bx1 - bx0 < by1 - by0:   # long side along y: notch at the y end nearest the JST
        cxw = (bx0 + bx1) / 2
        wire_rect = ([cxw - ww / 2, by0 - BATT_GAP - wl, cxw + ww / 2, by0] if abs(jy - by0) < abs(jy - by1)
                     else [cxw - ww / 2, by1, cxw + ww / 2, by1 + BATT_GAP + wl])
    else:
        cyw = (by0 + by1) / 2
        wire_rect = ([bx0 - BATT_GAP - wl, cyw - ww / 2, bx0, cyw + ww / 2] if abs(jx - bx0) < abs(jx - bx1)
                     else [bx1, cyw - ww / 2, bx1 + BATT_GAP + wl, cyw + ww / 2])
    print("battery %gx%gx%g: x %.1f..%.1f  y %.1f..%.1f, pocket %.1f deep, %.2f mm spare under %s" % (
        bl, bw, bt, bx0, bx1, by0, by1, BATT_POCKET_D, spare, who))
print("collisions:", issues or "none")

# ---- jscad ----
J = json.dumps
r3 = lambda a: [round(v, 3) for v in a]
common = """
var TILT = %s, Y_PIVOT = %s, Z_REAR = %s;
// board frame -> world: tilt about x around the PCB rear edge, then lift
function T(o) { return o.translate([0, -Y_PIVOT, 0]).rotateX(TILT).translate([0, Y_PIVOT, Z_REAR]); }
function rrect(c, r, rr) { return CAG.roundedRectangle({ center: c, radius: r, roundradius: rr, resolution: 32 }); }
""" % (TILT_DEG, round(Y_PIVOT, 4), Z_REAR)

bottom = """// GENERATED by build_case.py from the board. Edit build_case.py, not this file.
// Bottom tray. World frame: ergogen xy, z = 0 under the floor. Flat floor; the PCB sits on the
// pillars + corner ledges parallel to the sloped top edge; the switch plate drops in flush with the top.
%s
function main() {
    var floorT = %s, plateTop = %s, gap = %s, usbGap = %s, scoop = %s, collar = %s, usbMouth = %s;
    var cx = %s, cy = %s, OUT = %s, INN = %s;
    var yRearIn = %s, yRear = %s;
    var posts = %s, postR = %s, pilotR = %s, pilotD = %s, ledges = %s;
    var cuts = %s;   // [x, depth-centre below PCB, w, h] in board frame
    var batt = %s, wire = %s, battD = %s, battGap = %s;
    var outer = rrect([cx, cy], [OUT[0] / 2, OUT[1] / 2], OUT[2]);
    var inner = rrect([cx, cy], [INN[0] / 2, INN[1] / 2], INN[2]);
    var cavity = inner.extrude({ offset: [0, 0, 50] });
    var tray = outer.extrude({ offset: [0, 0, 40] }).subtract(cavity.translate([0, 0, floorT]));
    // anything above the plate top plane goes (walls end flush with the plate)
    var big = 400;
    var abovePlate = T(CSG.cube({ corner1: [cx - big, cy - big, plateTop], corner2: [cx + big, cy + big, plateTop + big] }));
    var belowPcb   = T(CSG.cube({ corner1: [cx - big, cy - big, -big], corner2: [cx + big, cy + big, 0] }));
    tray = tray.subtract(abovePlate);

    // supports: screw pillars + corner ledges, trimmed to the (tilted) PCB underside and
    // kept inside the cavity so nothing pokes through the walls
    var sup = null;
    for (var i = 0; i < posts.length; i++) {
        var c = CSG.cylinder({ start: [posts[i][0], posts[i][1], 0], end: [posts[i][0], posts[i][1], 30], radius: postR, resolution: 32 });
        sup = sup ? sup.union(c) : c;
    }
    for (var k = 0; k < ledges.length; k++) {
        var L = ledges[k];
        sup = sup.union(CSG.cube({ corner1: [L[0], L[1], 0], corner2: [L[2], L[3], 30] }));
    }
    tray = tray.union(sup.intersect(belowPcb).intersect(cavity));
    // collar around the USB port inside the rear wall, so the scoop has a back wall flush with the USB mouth
    if (collar) tray = tray.union(T(CSG.cube({ corner1: [collar[0], collar[1], -big], corner2: [collar[2], collar[3], collar[4]] })).intersect(cavity));
    for (var j = 0; j < posts.length; j++) {
        // pilot square to the tilted board (matches the screw axis), down the whole pillar and cut
        // flat at the floor top, so the floor stays closed
        var pilot = T(CSG.cylinder({ start: [posts[j][0], posts[j][1], 1], end: [posts[j][0], posts[j][1], -pilotD[j] - 1], radius: pilotR, resolution: 24 }));
        tray = tray.subtract(pilot.intersect(CSG.cube({ corner1: [posts[j][0] - 5, posts[j][1] - 5, floorT], corner2: [posts[j][0] + 5, posts[j][1] + 5, plateTop + 20] })));
    }

    // rear-wall windows: part outline + gap, in the board frame, then tilted with the board
    function wallSlab(prof, y0, y1) {   // profile drawn in (x, z) -> slab spanning y0..y1
        return prof.extrude({ offset: [0, 0, y1 - y0] }).rotateX(90).translate([0, y1, 0]);
    }
    function win(c, rr, y0, y1, g) {
        if (g === undefined) g = gap;
        return T(wallSlab(rrect([c[0], -c[1]], [c[2] / 2 + g, c[3] / 2 + g], rr), y0, y1));
    }
    tray = tray.subtract(win(cuts.usb, 1.2, (collar ? collar[1] : yRearIn) - 1, yRear + 1, usbGap));
    // cable-head scoop: recess from the outer face down to the USB mouth plane (flush with the port)
    tray = tray.subtract(T(wallSlab(rrect([cuts.usb[0], -cuts.usb[1]], [scoop[0] / 2, scoop[1] / 2], scoop[2]), usbMouth, yRear + 1)));
    tray = tray.subtract(win(cuts.rst, 0.6, yRearIn - 1, yRear + 1));
    tray = tray.subtract(win(cuts.pwr, 0.6, yRearIn - 1, yRear + 1));
    // battery pocket in the floor (cell + gap), plus a notch for its lead toward the JST
    if (batt) {
        var bg = battGap;
        tray = tray.subtract(CSG.cube({ corner1: [batt[0] - bg, batt[1] - bg, floorT - battD], corner2: [batt[2] + bg, batt[3] + bg, floorT + 0.01] }));
        tray = tray.subtract(CSG.cube({ corner1: [wire[0], wire[1], floorT - battD], corner2: [wire[2], wire[3], floorT + 0.01] }));
    }
    return tray;
}
""" % (common, FLOOR_T, PLATE_TOP, GAP, USB_GAP, J(USB_SCOOP), J(r3(collar) if collar else None), round(usb_mouth, 3), round(CX, 3), round(CY, 3), J(r3(OUTER)), J(r3(INNER)),
       round(Y_REAR_IN, 3), round(Y_REAR_OUT, 3), J([r3(p) for p in POSTS]), POST_R, PILOT_R, J([sc[3] for sc in screws]),
       J([r3(L) for L in ledges]), J({k: r3(c) for k, c in cut.items()}),
       J(r3(batt_rect) if batt_rect else None), J(r3(wire_rect) if wire_rect else None), BATT_POCKET_D, BATT_GAP)

plate = """// GENERATED by build_case.py from the board. Edit build_case.py, not this file.
// Switch plate in the board frame (z = 0 at the PCB underside): plate %s..%s, with a rim and
// spacer bosses underneath reaching down to the PCB top (z = %s). Pin reliefs are blind pockets
// from below; screw holes are countersunk from the top. Print it upside down.
// It drops inside the tray walls (%smm clearance per side).
%s
function main() {
    var cx = %s, cy = %s, pw = %s, ph = %s, pr = %s;
    var sw = %s, swCut = %s, stabs = %s, holes = %s, screwR = %s, cskR = %s, spacerR = %s, reliefs = %s;
    var lights = %s, lightR = %s;
    var plateT = %s, plateBot = %s, pcbTop = %s, rimW = %s, skin = %s;
    var S = { dx: %s, w: %s, h: %s, notchW: %s, notchD: %s, neckH: %s, cy: %s };
    var outline = rrect([cx, cy], [pw / 2, ph / 2], pr);

    // stabilizer cutout for a 2u key centred at the origin, in the stab frame: bar on the -y side,
    // wings offset S.cy toward it, notch on the +y end (rotated so -y points at the bar)
    function stabCut() {
        var c = null;
        for (var sgn = -1; sgn <= 1; sgn += 2) {
            var wing = CAG.rectangle({ center: [sgn * S.dx, S.cy], radius: [S.w / 2, S.h / 2] })
                .union(CAG.rectangle({ center: [sgn * S.dx, S.cy + S.h / 2 + S.notchD / 2 - 0.01], radius: [S.notchW / 2, S.notchD / 2] }))
                .union(CAG.rectangle({ corner1: [Math.min(sgn * S.dx, 0), S.cy - S.neckH / 2], corner2: [Math.max(sgn * S.dx, 0), S.cy + S.neckH / 2] }));
            c = c ? c.union(wing) : wing;
        }
        return c;
    }
    var holesCag = null;
    function addHole(h) { holesCag = holesCag ? holesCag.union(h) : h; }
    for (var i = 0; i < sw.length; i++) {
        addHole(CAG.rectangle({ center: sw[i], radius: [swCut / 2, swCut / 2] }));
    }
    // status LED light holes (through), under a keycap-gap crossing
    for (var l = 0; l < lights.length; l++) {
        addHole(CAG.circle({ center: lights[l], radius: lightR, resolution: 24 }));
    }
    for (var s = 0; s < stabs.length; s++) {
        addHole(stabCut().rotateZ(stabs[s][2]).translate([stabs[s][0], stabs[s][1]]));
    }
    // THT pins poking up through the PCB get blind pockets from below (plate top stays closed)
    var pockets = null;
    for (var k = 0; k < reliefs.length; k++) {
        var r = reliefs[k];
        var pk = CAG.rectangle({ corner1: [r[0], r[1]], corner2: [r[2], r[3]] });
        pockets = pockets ? pockets.union(pk) : pk;
    }
    var screwHoles = null;
    for (var j = 0; j < holes.length; j++) {
        var sh = CAG.circle({ center: holes[j], radius: screwR, resolution: 32 });
        screwHoles = screwHoles ? screwHoles.union(sh) : sh;
    }

    // pin pockets are blind from below (plate top stays closed); screw holes go through with a
    // 90 deg countersink on top for the bevel heads
    var plateTop = plateBot + plateT;
    var plate = outline.subtract(holesCag).subtract(screwHoles)
        .extrude({ offset: [0, 0, plateT] }).translate([0, 0, plateBot])
        .subtract(pockets.extrude({ offset: [0, 0, plateT - skin + 0.01] }).translate([0, 0, plateBot - 0.01]));
    for (var c = 0; c < holes.length; c++) {
        plate = plate.subtract(CSG.cylinder({ start: [holes[c][0], holes[c][1], plateTop + 0.2], end: [holes[c][0], holes[c][1], plateTop - (cskR - screwR)],
            radiusStart: cskR + 0.2, radiusEnd: screwR, resolution: 32 }));
    }
    // underneath: a rim along the edge and spacer bosses at the screws, down to the PCB top
    var rim = outline.subtract(rrect([cx, cy], [pw / 2 - rimW, ph / 2 - rimW], Math.max(pr - rimW, 0.3)));
    var bosses = null;
    for (var b = 0; b < holes.length; b++) {
        var bc = CAG.circle({ center: holes[b], radius: spacerR, resolution: 32 });
        bosses = bosses ? bosses.union(bc) : bc;
    }
    var under = rim.union(bosses).subtract(holesCag).subtract(screwHoles).subtract(pockets)
        .extrude({ offset: [0, 0, plateBot - pcbTop + 0.01] }).translate([0, 0, pcbTop]);
    return plate.union(under);
}
""" % (round(PLATE_TOP - PLATE_T, 3), PLATE_TOP, PCB_T, PLATE_TOL, common,
       round(CX, 3), round(CY, 3), round(pw, 3), round(ph, 3), round(pr, 3),
       J([r3(s) for s in switches]), SW_CUT, J([r3(s) for s in stabs]), J([r3(p) for p in POSTS]),
       SCREW_R, CSK_R, SPACER_R, J([r3(r) for r in reliefs]), J([r3(l) for l in lights]), LED_HOLE_R, PLATE_T, round(PLATE_TOP - PLATE_T, 3), PCB_T, RIM_W, PLATE_SKIN,
       STAB_DX, STAB_W, STAB_H, STAB_NOTCH_W, STAB_NOTCH_D, STAB_NECK_H, STAB_CUT_Y)

open(os.path.join(HERE, "case_bottom.jscad"), "w").write(bottom)
open(os.path.join(HERE, "case_plate.jscad"), "w").write(plate)

json.dump({"tilt_deg": TILT_DEG, "y_pivot": Y_PIVOT, "z_rear": Z_REAR,
           "pcb": {"outline": outline, "poly_holes": poly_holes,
                   "holes": [[p[0], p[1], SCREW_R] for p in POSTS], "z0": 0, "z1": PCB_T},
           "boxes": boxes,
           # world-frame parts (not tilted): the battery sitting in its floor pocket
           "world_boxes": ([{"name": "battery", "kind": "battery",
                             "min": [batt_rect[0], batt_rect[1], FLOOR_T - BATT_POCKET_D],
                             "max": [batt_rect[2], batt_rect[3], FLOOR_T - BATT_POCKET_D + BATTERY[0]]}] if batt_rect else [])},
          open(os.path.join(HERE, "assembly.json"), "w"))
print("2u stabilizers at:", stabs)
print("M2 countersunk screws from the top (self-tapping into the pillars):")
for (px, py, L, depth, top) in screws:
    print("  (%.1f, %.1f): M2x%d, %.1f mm of thread in a %.2f tall pillar (pilot %.1f deep)" % (
        px, py, L, L - PLATE_TOP, top, depth))
print("wrote case_bottom.jscad, case_plate.jscad, assembly.json (%d boxes)" % len(boxes))
