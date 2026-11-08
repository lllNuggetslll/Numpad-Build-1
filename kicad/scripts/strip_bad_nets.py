# strip_bad_nets.py in.kicad_pcb drc.rpt out.kicad_pcb  (KiCad 8 python)
# Deletes the tracks of every net in a clearance/short/mask-bridge/hole/edge error and locks the rest, so the
# next keepout_dsn.py + freerouting pass re-routes only those nets. Import the .ses into the stripped board.
import pcbnew, sys, re
b = pcbnew.LoadBoard(sys.argv[1]); txt = open(sys.argv[2], encoding="utf-8").read()
bad = set()
for bl in re.split(r"\n(?=\[)", txt):
    if re.match(r"\[(clearance|shorting_items|solder_mask_bridge|hole_clearance|copper_edge_clearance|tracks_crossing)\]", bl):
        bad |= set(re.findall(r"(?:Track|Via) \[([^\]]+)\]", bl))
print("re-route nets:", sorted(bad))
for t in list(b.GetTracks()):
    if t.GetNetname() in bad: b.Remove(t)
    else: t.SetLocked(True)
b.Save(sys.argv[3])
