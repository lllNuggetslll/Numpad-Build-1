# keepout_dsn.py in.kicad_pcb out.dsn  (KiCad 8 python)
# Export a DSN with rule-area keepouts over every no-net pad / NPTH hole (freerouting 1.4.5 ignores them).
import pcbnew, sys, math
b = pcbnew.LoadBoard(sys.argv[1])
M = 0.3   # hole clearance 0.25 + margin
n = 0
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode() != 0:
            continue
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
        c = p.GetPosition(); cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
        bb = p.GetBoundingBox()
        if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
            r = pcbnew.ToMM(max(p.GetSize().x, p.GetDrillSize().x)) / 2 + M
            pts = [(cx + r / math.cos(math.pi / 16) * math.cos(2 * math.pi * k / 16),
                    cy + r / math.cos(math.pi / 16) * math.sin(2 * math.pi * k / 16)) for k in range(16)]
        else:
            x0, y0 = pcbnew.ToMM(bb.GetLeft()) - M, pcbnew.ToMM(bb.GetTop()) - M
            x1, y1 = pcbnew.ToMM(bb.GetRight()) + M, pcbnew.ToMM(bb.GetBottom()) + M
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        ol = z.Outline(); ol.NewOutline()
        for x, y in pts:
            ol.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        b.Add(z); n += 1
print("keepouts", n)
print("dsn", pcbnew.ExportSpecctraDSN(b, sys.argv[2]))
