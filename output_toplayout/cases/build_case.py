# Generates the case from the routed board (single source of truth for the stack-up):
#   case_bottom.jscad  tilted tray: flat floor, PCB parallel to the sloped top edge,
#                      screw pillars + corner support ledges cut to the PCB underside,
#                      rear-wall windows for USB-C / reset / power.
#   case_plate.jscad   switch plate (flat, print orientation), inset inside the tray walls.
#   assembly.json      PCB + part boxes for viewer.html and the collision report below.
# Run with KiCad's python:  "C:/Program Files/KiCad/8.0/bin/python.exe" build_case.py
# then render each .jscad with @jscad/cli@1 (see CLAUDE.md).
#
# Frames: "board frame" = ergogen xy (x = kicad_x, y = -kicad_y), z = 0 at the PCB underside,
# PCB flat. "world" = case frame, z = 0 under the floor. World = board frame rotated about the
# x axis by TILT_DEG around the PCB's rear edge (y = Y_PIVOT), then lifted by Z_REAR.
import json, math, os, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "..", "pcbs", "not_about_money.kicad_pcb")

# ---- case ----
FLOOR_T = 1.0
TILT_DEG = 2.37            # rear higher; same slope as the earlier 5mm-over-120.9mm shell
FLOOR_CLEAR = 0.5          # min gap between the lowest part and the floor
CX, CY = 128.5, -52.5      # board centre
OUTER = (82.9, 120.9, 3.45)  # shell w, h, corner r (from the outline DXF)
INNER = (80.5, 118.5, 2.25)  # cavity w, h, corner r
POSTS = [(109.5, -90.5), (109.5, -33.5), (128.5, -52.5), (147.5, -90.5), (147.5, -14.5)]
POST_R, SCREW_R = 3.0, 1.1
LEDGE_W, LEDGE_ARM = 1.6, 10.0   # corner support ledges: width in from the wall, arm length
GAP = 0.4                  # wiggle room around each wall cutout, per side

# ---- plate ----
PCB_T = 1.6
PLATE_T = 1.2
PLATE_TOP = PCB_T + 2.2    # plate top above the PCB underside (Gateron LP: 2.2 above PCB top)
PLATE_TOL = 0.2            # plate edge to tray wall, per side
SW_CUT = 14.0              # switch cutout
PIN_RELIEF = 0.4           # clearance around THT pins poking up through the PCB

# ---- part heights below the PCB (board frame, positive = depth below the underside) ----
SOCKET_H = 1.85            # Gateron LP HS 2.0 socket (KS-2P02B01-02)
DIODE_H = 1.15             # SOD-123
RST_H, RST_PLUNGER = 1.7, (0.35, 1.35)   # EVQ-PUx02K body; plunger depth range
PWR_H, PWR_LEVER = 1.4, (0.3, 1.1)       # Alps SSSS811101 body; lever depth range
JST_H = 4.8                # JST PH S2B-PH-K-S side entry
HEADER_GAP, NANO_T, NANO_PARTS_H = 2.5, 1.0, 1.0
USB_W, USB_H, USB_D, USB_BELOW_NANO = 8.94, 3.26, 7.35, 2.2

mm = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
edge = b.GetBoardEdgesBoundingBox()
Y_PIVOT = -mm(edge.GetTop())          # PCB rear edge (ergogen y)
Y_REAR_IN = CY + INNER[1] / 2
Y_REAR_OUT = CY + OUTER[1] / 2

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

switches, cut = [], {}
for f in b.GetFootprints():
    ref, fid = f.GetReference(), f.GetFPIDAsString()
    x, y = mm(f.GetPosition().x), mm(f.GetPosition().y)
    top = -PCB_T
    if "switch_gateron" in fid:
        switches.append([x, -y, f.GetOrientationDegrees()])
        box(ref, "switch", x - 7.25, y - 7.25, x + 7.25, y + 7.25, top, top - 3.0)
        box(ref + "_top", "switch", x - 6.6, y - 6.6, x + 6.6, y + 6.6, top - 3.0, top - 5.0)
        box(ref + "_stem", "stem", x - 2.75, y - 1.5, x + 2.75, y + 1.5, top - 5.0, top - 6.6)
        t, s = pads(f, pth), pads(f, smd)
        box(ref + "_socket", "socket", t[0] - 0.3, t[1], t[2] + 0.3, s[3], 0, SOCKET_H)
        continue
    if "mounting_hole" in fid:
        continue
    # THT pins of side-B parts poke up through the PCB: relieve them in the plate
    for p in f.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            bb = p.GetBoundingBox()
            reliefs.append([mm(bb.GetLeft()) - PIN_RELIEF, -mm(bb.GetBottom()) - PIN_RELIEF,
                            mm(bb.GetRight()) + PIN_RELIEF, -mm(bb.GetTop()) + PIN_RELIEF])
    if "diode" in fid:
        s = pads(f, smd)
        cx, cy = (s[0] + s[2]) / 2, (s[1] + s[3]) / 2
        hx, hy = (1.35, 0.8) if (s[2] - s[0]) > (s[3] - s[1]) else (0.8, 1.35)
        box(ref, "diode", cx - hx, cy - hy, cx + hx, cy + hy, 0, DIODE_H)
    elif "mcu_nice_nano" in fid:
        n0 = HEADER_GAP; n1 = n0 + NANO_T             # nano PCB depth range
        top_y = y - 16.51
        box("nano", "nano", x - 9.0, top_y, x + 9.0, top_y + 33.3, n0, n1)
        box("nano_parts", "nano_parts", x - 6.5, top_y + 6.0, x + 6.5, top_y + 26.0, n1, n1 + NANO_PARTS_H)
        usb_cx = x - (3.556 - 3.81) / 2               # socket outline mirrored onto side B
        mouth = y - 18.034
        u1 = n1 + USB_BELOW_NANO
        box("usb_c", "usb", usb_cx - USB_W / 2, mouth, usb_cx + USB_W / 2, mouth + USB_D, u1 - USB_H, u1)
        cut["usb"] = (usb_cx, u1 - USB_H / 2, USB_W, USB_H)
        for p in f.Pads():
            if pth(p):
                px, py = mm(p.GetPosition().x), mm(p.GetPosition().y)
                box("hdr", "header", px - 1.25, py - 1.25, px + 1.25, py + 1.25, 0, HEADER_GAP)
    elif "reset_switch" in fid:
        box(ref, "part", x - 2.35, y - 1.75, x + 2.35, y + 1.75, 0, RST_H)
        box(ref + "_plunger", "actuator", x - 1.3, y - 2.75, x + 1.3, y - 1.75, *RST_PLUNGER)
        cut["rst"] = (x, sum(RST_PLUNGER) / 2, 2.6, RST_PLUNGER[1] - RST_PLUNGER[0])
    elif "power_switch" in fid:
        box(ref, "part", x - 3.4, y - 1.3, x + 3.4, y + 1.3, 0, PWR_H)
        # lever drawn in the "on" position; the cutout covers its full x +-1.65 travel
        box(ref + "_lever", "actuator", x + 0.2, y - 2.9, x + 1.5, y - 1.3, *PWR_LEVER)
        cut["pwr"] = (x, sum(PWR_LEVER) / 2, 3.3, PWR_LEVER[1] - PWR_LEVER[0])
    elif "jst" in fid:
        fab = [1e9, 1e9, -1e9, -1e9]
        for g in f.GraphicalItems():
            if g.GetLayerName() == "B.Fab":
                bb = g.GetBoundingBox()
                fab = [min(fab[0], mm(bb.GetLeft())), min(fab[1], mm(bb.GetTop())),
                       max(fab[2], mm(bb.GetRight())), max(fab[3], mm(bb.GetBottom()))]
        box(ref, "part", fab[0], fab[1], fab[2], fab[3], 0, JST_H)

# ---- tilt: lift the board until the lowest part clears the floor ----
th = math.radians(TILT_DEG)
def world_z(y, z, z_rear):
    return z_rear + (y - Y_PIVOT) * math.sin(th) + z * math.cos(th)
need = 0
for bx in boxes:
    if bx["max"][2] <= 0.01:
        for yy in (bx["min"][1], bx["max"][1]):
            need = max(need, FLOOR_T + FLOOR_CLEAR - world_z(yy, bx["min"][2], 0))
Z_REAR = math.ceil(need * 10) / 10
front_y = -mm(edge.GetBottom())
print("PCB underside: rear edge z=%.2f, front edge z=%.2f" % (Z_REAR, world_z(front_y, 0, Z_REAR)))
print("plate/wall top: rear z=%.2f, front z=%.2f" % (world_z(Y_REAR_OUT, PLATE_TOP, Z_REAR),
                                                    world_z(CY - OUTER[1] / 2, PLATE_TOP, Z_REAR)))

# ---- corner ledges (board-frame xy rects) ----
ix0, ix1 = CX - INNER[0] / 2, CX + INNER[0] / 2
iy0, iy1 = CY - INNER[1] / 2, CY + INNER[1] / 2
ledges = []
for (xw, sx) in ((ix0, 1), (ix1, -1)):
    for (yw, sy) in ((iy0, 1), (iy1, -1)):
        ledges.append(sorted([xw - sx, xw + sx * LEDGE_ARM]) + sorted([yw - sy, yw + sy * LEDGE_W]))
        ledges.append(sorted([xw - sx, xw + sx * LEDGE_W]) + sorted([yw - sy, yw + sy * LEDGE_ARM]))
ledges = [[r[0], r[2], r[1], r[3]] for r in ledges]   # -> [x0, y0, x1, y1]

# ---- collision report (parts under the PCB vs posts and ledges) ----
issues = []
for bx in boxes:
    if bx["max"][2] > 0.01:
        continue
    for (px, py) in POSTS:
        nx = min(max(px, bx["min"][0]), bx["max"][0]); ny = min(max(py, bx["min"][1]), bx["max"][1])
        if math.hypot(px - nx, py - ny) < POST_R:
            issues.append("%s overlaps standoff (%.1f, %.1f)" % (bx["name"], px, py))
    for L in ledges:
        if bx["min"][0] < L[2] and bx["max"][0] > L[0] and bx["min"][1] < L[3] and bx["max"][1] > L[1]:
            issues.append("%s overlaps corner ledge %s" % (bx["name"], [round(v, 1) for v in L]))
print("collisions:", issues or "none")

# ---- jscad ----
J = json.dumps
common = """
var TILT = %s, Y_PIVOT = %s, Z_REAR = %s;
// board frame -> world: tilt about x around the PCB rear edge, then lift
function T(o) { return o.translate([0, -Y_PIVOT, 0]).rotateX(TILT).translate([0, Y_PIVOT, Z_REAR]); }
function rrect(c, r, rr) { return CAG.roundedRectangle({ center: c, radius: r, roundradius: rr, resolution: 32 }); }
""" % (TILT_DEG, round(Y_PIVOT, 4), Z_REAR)

bottom = """// GENERATED by build_case.py from the routed board. Edit build_case.py, not this file.
// Bottom tray. World frame: ergogen xy, z = 0 under the floor. Flat floor; the PCB sits on the
// pillars + corner ledges parallel to the sloped top edge; the switch plate drops in flush with the top.
%s
function main() {
    var floorT = %s, plateTop = %s, gap = %s;
    var cx = %s, cy = %s, OUT = %s, INN = %s;
    var yRearIn = %s, yRear = %s;
    var posts = %s, postR = %s, screwR = %s, ledges = %s;
    var cuts = %s;   // [x, depth-centre below PCB, w, h] in board frame
    var outer = rrect([cx, cy], [OUT[0] / 2, OUT[1] / 2], OUT[2]);
    var inner = rrect([cx, cy], [INN[0] / 2, INN[1] / 2], INN[2]);
    var tray = outer.extrude({ offset: [0, 0, 40] })
        .subtract(inner.extrude({ offset: [0, 0, 50] }).translate([0, 0, floorT]));
    // anything above the plate top plane goes (walls end flush with the plate)
    var big = 400;
    var abovePlate = T(CSG.cube({ corner1: [cx - big, cy - big, plateTop], corner2: [cx + big, cy + big, plateTop + big] }));
    var belowPcb   = T(CSG.cube({ corner1: [cx - big, cy - big, -big], corner2: [cx + big, cy + big, 0] }));
    tray = tray.subtract(abovePlate);

    // supports: screw pillars + corner ledges, trimmed to the (tilted) PCB underside
    var sup = null;
    for (var i = 0; i < posts.length; i++) {
        var c = CSG.cylinder({ start: [posts[i][0], posts[i][1], 0], end: [posts[i][0], posts[i][1], 30], radius: postR, resolution: 32 });
        sup = sup ? sup.union(c) : c;
    }
    for (var k = 0; k < ledges.length; k++) {
        var L = ledges[k];
        sup = sup.union(CSG.cube({ corner1: [L[0], L[1], 0], corner2: [L[2], L[3], 30] }));
    }
    tray = tray.union(sup.intersect(belowPcb));
    for (var j = 0; j < posts.length; j++) {
        tray = tray.subtract(CSG.cylinder({ start: [posts[j][0], posts[j][1], -1], end: [posts[j][0], posts[j][1], 40], radius: screwR, resolution: 32 }));
    }

    // rear-wall windows: part outline + gap, in the board frame, then tilted with the board
    function wallSlab(prof, y0, y1) {   // profile drawn in (x, z) -> slab spanning y0..y1
        return prof.extrude({ offset: [0, 0, y1 - y0] }).rotateX(90).translate([0, y1, 0]);
    }
    function win(c, rr, extraW, extraH, y0, y1) {
        return T(wallSlab(rrect([c[0], -c[1]], [c[2] / 2 + extraW, c[3] / 2 + extraH], rr), y0, y1));
    }
    tray = tray.subtract(win(cuts.usb, 1.2, gap, gap, yRearIn - 1, yRear + 1));
    // outer pocket so a USB-C plug overmold (~12 x 6.5) gets close enough to seat
    tray = tray.subtract(T(wallSlab(rrect([cuts.usb[0], -cuts.usb[1]], [6.4, 3.4], 2.0), yRear - 0.6, yRear + 1)));
    tray = tray.subtract(win(cuts.rst, 0.6, gap, gap, yRearIn - 1, yRear + 1));
    tray = tray.subtract(win(cuts.pwr, 0.6, gap, gap, yRearIn - 1, yRear + 1));
    // nail scoop around the power lever
    tray = tray.subtract(T(wallSlab(rrect([cuts.pwr[0], -cuts.pwr[1]], [3.2, 1.9], 1.2), yRear - 0.5, yRear + 1)));
    return tray;
}
""" % (common, FLOOR_T, PLATE_TOP, GAP, CX, CY, J(OUTER), J(INNER), Y_REAR_IN, Y_REAR_OUT,
       J(POSTS), POST_R, SCREW_R, J([[round(v, 3) for v in L] for L in ledges]),
       J({k: [round(v, 3) for v in c] for k, c in cut.items()}))

plate = """// GENERATED by build_case.py from the routed board. Edit build_case.py, not this file.
// Switch plate, flat in the board frame (print orientation): z = 0 at the PCB underside, so the
// plate spans z %s..%s. It drops inside the tray walls (%smm clearance per side).
%s
function main() {
    var cx = %s, cy = %s, INN = %s, tol = %s;
    var sw = %s, swCut = %s, holes = %s, screwR = %s, reliefs = %s;
    var shape = rrect([cx, cy], [INN[0] / 2 - tol, INN[1] / 2 - tol], INN[2] - tol);
    for (var i = 0; i < sw.length; i++) {
        shape = shape.subtract(CAG.rectangle({ center: [0, 0], radius: [swCut / 2, swCut / 2] })
            .rotateZ(sw[i][2]).translate([sw[i][0], sw[i][1]]));
    }
    for (var j = 0; j < holes.length; j++) {
        shape = shape.subtract(CAG.circle({ center: holes[j], radius: screwR, resolution: 32 }));
    }
    for (var k = 0; k < reliefs.length; k++) {
        var r = reliefs[k];
        shape = shape.subtract(CAG.rectangle({ corner1: [r[0], r[1]], corner2: [r[2], r[3]] }));
    }
    return shape.extrude({ offset: [0, 0, %s] }).translate([0, 0, %s]);
}
""" % (PLATE_TOP - PLATE_T, PLATE_TOP, PLATE_TOL, common, CX, CY, J(INNER), PLATE_TOL,
       J([[round(v, 3) for v in s] for s in switches]), SW_CUT, J(POSTS), SCREW_R,
       J([[round(v, 3) for v in r] for r in reliefs]), PLATE_T, PLATE_TOP - PLATE_T)

open(os.path.join(HERE, "case_bottom.jscad"), "w").write(bottom)
open(os.path.join(HERE, "case_plate.jscad"), "w").write(plate)

ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps); ol = ps.Outline(0)
json.dump({"tilt_deg": TILT_DEG, "y_pivot": Y_PIVOT, "z_rear": Z_REAR,
           "pcb": {"outline": [[mm(ol.CPoint(i).x), -mm(ol.CPoint(i).y)] for i in range(ol.PointCount())],
                   "holes": [[px, py, SCREW_R] for (px, py) in POSTS], "z0": 0, "z1": PCB_T},
           "boxes": boxes}, open(os.path.join(HERE, "assembly.json"), "w"))
print("wrote case_bottom.jscad, case_plate.jscad, assembly.json (%d boxes)" % len(boxes))
