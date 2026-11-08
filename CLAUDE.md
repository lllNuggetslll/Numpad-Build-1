# Numpad (ergogen, "not about money" base)

Low-profile 21-key numpad: 4 columns × 6 rows, nice!nano (wireless, ZMK), JST PH battery,
Gateron low-profile **hotswap** switches. Generated with ergogen; routed with freerouting; checked in KiCad 8.

> **Keep this file updated.** Whenever you change `config.yaml`, the layout, the build/route/case
> workflow, or learn a non-obvious fact (a gotcha, a coordinate, a tool version), update the relevant
> section here before you finish — this file is the handoff between chat instances. The user hand-edits
> boards between sessions, so treat coordinates here as a starting point and re-measure the current board
> (`pcbnew`) / re-parse the current outline DXF rather than trusting stale numbers.

## Design rules / user preferences

- **Switches** are on the front. Hotswap sockets, diodes and every other component go on the
  **back (side B)**: the nice!nano, power switch, reset button and JST connector. Keep new parts on B
  unless the user says otherwise.
- **Top edge layout:** the nice!nano, on/off switch and reset button all point **up** out of the top edge.
  - nice!nano: USB at the top edge, left of center (KiCad x=121.44, y=11.75, rotation 0; moved 1.5 toward the
    edge on 2026-10-04 so its board edge is flush with the PCB edge and the USB-C pokes 0.96 past it).
  - Power switch: 20mm from the right edge (x=148.5), `rotate: 90` so the lever points up.
  - Reset button: between the controller and the power switch (x=137.2).
- **Keycap spacing:** 1u keycaps are 18mm on a 19mm pitch, so there's a 1mm gap between caps. The user
  wants the **same 1mm gap from the outer keycaps to the case wall**. That's why `board_expand: 0.25`:
  PCB edge 0.25 + wall tolerance 0.25 = 1mm from the keycap edge. The MCU and power shifts are written as
  `... - (2 - board_expand)` so they follow the edge.
- **Stabilizers:** Gateron LP plate-mount KS-57B210T (spec: gateron.com/u_file/2311/22/file/
  GATERONLowProfilePlateMountedStabilizer2U-KS-57B210T.pdf).
  - **The user's STEP model is the authority:** `C:/Users/Nuggets/Downloads/lowprofilestabilizer/low profile
    stabilizer..stp`. It holds 5 solids in one frame: 2 housings, 2 actuators, the wire. Parse it with a small
    python script that walks the entity references from each MANIFOLD_SOLID_BREP down to its VERTEX_POINTs.
    Values below use a stem-centred frame with the bar on the -y side.
    - Housings 24.00 apart; 6.00 wide at their crush ribs. **How it mounts** (STEP, 2026-10-05): at the bar
      end a tongue runs under the plate (top at z 4.55, out to y -9.7) and two clip legs pass through the plate
      out to y -6.80; at the far end a 1.66-wide latch tab catches the plate underside out to y +5.70. The flange
      ends sit at z 5.65, 0.1 below the nominal plate top, so a 1.2 plate is clamped with 0.1 preload. So you
      hook the bar end under the plate and snap the far end down.
    - **Plate cutout = Gateron's suggested mounting** (since 2026-10-05): wing y -6.845..+5.655, notch 1.7 × 1.15
      on the **bar end** (out to the bar line), neck 2.5 tall at y -2.64..-0.14. The figure is to scale; the
      offsets are read off it. gmsh booleans of the STEP solids vs this plate: only the 0.1 flange-clamp and a
      0.05 latch overlap. The old cutout (-6.5..+6.0, 1.0 notch on the far end, neck centred at -0.25) cut 0.3
      into both clip legs and left the latch 0.3 short of the plate edge. Its "not-to-scale drawing" assumption
      and the notch side were wrong. Script: gmsh 4.15 (`pip download gmsh`, unzip the wheel's
      `gmsh-4.15.dll` next to `gmsh.py`); `occ.importShapes` the STEP, plate = box minus cutout,
      `occ.intersect` per solid, `getMass` = overlap volume.
    - Housing below the plate: x ±2.93, **y -9.70..+5.13**, down to 4.45 below the plate top.
    - **Wire bar:** r 0.5 at y -7.975. Its centre sits 0.725 below the plate underside, so with our 1.3
      plate-PCB gap its bottom clears the PCB top by 0.075 (the PCB bar slot is now just margin).
  - **Gateron drawing** (the spec PDF's last page, vector; render with pymupdf; the user's copy is
    `C:/Users/Nuggets/Downloads/GATERONLowProfilePlateMountedStabilizer2U-KS-57B210T.pdf`), checked 2026-10-05: housings
    24.00±0.15 apart; flange 1.20 thick; housing 4.05 above / 4.45 below the plate top (= STEP z 1.3..9.8, so
    **STEP plate top = z 5.75**, stab centre x 60); plate 1.20±0.1; clip span 12.40. Suggested plate cutout
    6.00 × 12.50 with a 1.70 notch (now followed exactly, see below). Actuator top **7.70**
    above the plate top in section A-A (the STEP's actuators sit 0.4 lower, at 7.30). The switch stem is 6.40
    above the plate, so the free actuator reaches the keycap; whether it follows the full 3.0 down isn't drawn
    → test-fit. 2u keycaps need stab mounts 24 apart.
  - With the 2.5 plate (2026-10-05) the housings hang 0.35 below the PCB underside, 0.30 inside every PCB
    cutout edge (point-in-polygon re-check on `assembly.json`); the bar no longer enters the PCB.
  - **PCB cutout per 2u key** (`_stab_holes` → `_pcb_outline`):
    - Two housing holes 6.5×15.45, offset 2.275 toward the bar, joined by a 1.6-wide bar slot at 7.975.
    - **Bars point inward** (toward the board centre). Outward, the housing holes break the PCB edge and the
      slot would cut a strip loose.
  - **2u switch footprints:** separate `key_switch_0` (c1_r6, `rotate: 0`) and `key_switch_tall`
    (c4_r3/c4_r5, `rotate: 90`) entries, both with `outer_pad_width_*: 1.6`, so the socket pads clear the
    cutouts. The rotations were picked by DRC-testing all four; the cross stem doesn't care.
  - **Tall-key diodes (KS-33 board, fixed 2026-11-07):** every diode sits at `shift: [7.1, 1.25]`, but
    `key_switch_tall` (`rotate: 90`) turns the socket onto that spot. The old D18/D19 had pad 2 over the
    socket's Ø3 drill and their body under the socket body. DRC missed it (same net c4_rN; the diode footprint has no courtyard), and so did
    `build_case.py`, which had no part-vs-part check then (added 2026-11-07, see "JST battery connector move"). Now `diodes_tall` (`[matrix_c4_r3, matrix_c4_r5]`,
    `shift: [-5.0, 1.25]`) puts them under the switch's left half at KiCad x 152.0: 1.60 to the centre pad,
    1.58 to the bar slot, 1.67 to the centre post. Ergogen renumbered them: **D20 = "Enter" (c4_r5), D21 = "+"
    (c4_r3)**; the old D20/D21 (c4_r2/c4_r1) are now D18/D19. The KS-33G board was already clear and has no
    `diodes_tall`.
    - **The user already has boards of the old revision** (commit 8859cc4's board). Bodge given 2026-11-07:
      leave D18/D19 empty. Fit the sockets normally, then put a SOD-123 (or 1N4148) in the strip between the
      socket and the right board edge. Its cathode (band) goes on a scraped spot of the row trace (B.Cu,
      x 165.05; R5 at y ≈ 79.6, R3 at y ≈ 41.6, KiCad coords), and a short wire runs from its anode to the
      socket's pad-2 solder tab (x 161.5..164.0, y 82.75..85.3 / 44.75..47.3). Pad 1 = cathode = row on these
      footprints. Under-PCB room there is ~3.6 (S20) / ~5 (S21).
      - The 2 Oct (d0959ac) and 5 Oct (2b086c1) gerbers route these nets identically. The R5/R3 edge traces
        are confirmed in the gerber B_Cu (X165048800).
      - When drawing the back for hand work, **mirror it** (render.py's bottom view is see-through from
        the front, so the right edge stays on the right). The user was misled by the unmirrored picture.
      - The only plated rings near the tall keys are the socket holes (pad 1 = column C4, pad 2 = c4_rN) and
        the no-net Ø5.1 centre hole. No ring is on the row net.
      - Two options were given (re-checked against the parts 2026-11-07, picture `draw_back2.py` in scratch).
        (a) Skip the socket on these 2 keys and solder the switch pins straight into the Ø3 plated rings. D18's
        pad 2 is ~60% over the open Ø3 hole (pad x 163.5..164.7 vs hole edge 164.25), so use an **axial
        1N4148** instead: anode lead into the pad-2 ring beside the switch pin (it also fills the gap), cathode
        to D18/D19 pad 1 (row). Trim the lead flush on the front or it lifts the switch.
        (b) Keep the socket: a bodge diode with its band end toward D13's (S20) or D15's (S21) band end
        (row-5/row-3 cathode, back, x 145.1), plus a wire to the socket's pad-2 tab. **The stab housing hole
        (x 147..162.45, y 75.25..81.75 for S20, 37.25..43.75 for S21) sits between them**, and the housing hangs
        0.35 below the PCB there. Route through the clear strip y 81.75..87.7 (S20; S21 = -38), x 149.82..160.58:
        diode lying at y ≈ 84 with its anode on the tab (x 161.5), wire across the 1.6 bar slot (x 148.2..149.8;
        the stab bar stays above the PCB) to D13's pad 1 (y 81.4). Don't run down toward S12/S14's tab1
        (x 143.2..145.75, y 85.5..88), which is c3_rN.
  - **Screws moved for the bars:** front-left → (128.5, 90.5) (`ref: matrix_c3_r6`, past the end of the "0"
    key's bar); front-right → (147.5, 71.5) (one row back). See the case section.
- **Low-battery LED (the one exception to "everything on B"):** `battery_led` is a 0603 LED on the
  **front** at the keycap-gap crossing "E" (KiCad 128.5, 71.5; between c2/c3 and r4/r5). The plate has a
  3.8×2.0 counterbore (blind pocket from below, 0.6 deep) over it, which leaves 1.9 of room, so any 0603
  LED up to ~1.7 tall fits. Planned part: Lite-On LTST-C191KRKT (red, 0.55). There is a Ø1.8 through hole
  in the middle (`LED_HOLE_R`, `LED_POCKET`). Its 1k resistor `battery_led_resistor` sits on B directly under
  it. Circuit: P0 → R → LED_A → LED → GND. Both use `footprints/custom/smd_0603.js`.
  - Other free crossings, each with ≥3.17mm to the nearest pad: (109.5,14.5), (147.5,33.5), (109.5,52.5),
    (109.5,71.5). (147.5,71.5) and (128.5,90.5) now hold screws. The other crossings hold screws, an MCU
    pin or the JST connector.
- Use hotswap switches (`ceoloide/switch_gateron_ks27_ks33`, `hotswap: true`, `solder: false`), not choc.
- Show the user a quick prototype image before a big layout change.
- The user has KiCad 8 (and 10) installed. Drive it through its bundled Python (`pcbnew`) and `kicad-cli`.
  - **The user views boards in the KiCad 10 GUI.** Open boards for them with
    `C:\Program Files\KiCad\10.0\bin\pcbnew.exe`, never the KiCad 8 GUI.
  - Opening KiCad 8's GUI rewrites `numpad.kicad_pro` in v8 format (meta version 3 → 1). On close it also
    writes `numpad.kicad_prl` with numeric `visible_items`, which KiCad 10 reads as "show only the outline".
    Fix (2026-11-07): restore `.kicad_pro` from git and copy `numpad_ks33g.kicad_prl` (KiCad 10 format, named
    items) with its `filename` changed. KiCad 8's headless `pcbnew`/`kicad-cli` don't touch these files.

## KS-33G variant (Low Profile 3.0, added 2026-11-01)

A second PCB, `numpad_ks33g`, for Gateron **KS-33G** switches. The source is the user's spec
`C:/Users/Nuggets/Downloads/GATERONKS-33LowProfileSilent30MechanicalRedSwitchKS-33GJH10B045NW-X5B.pdf`; the
drawing is page 9, vector with no dimension text, so render it with pymupdf.
- **Same as KS-33:** 14.00 plate cutout, flange underside (plate top) **2.50** above the seat, 1.20 plate, 13.75
  upper housing. So the plate, stabs and case are unchanged. Differences: flange 14.60, stem top 8.95 (12.65 overall),
  travel 3.20 ±0.2, 45 ±15 gf. **Centre post 3.70 below the seat** (vs 3.25). Ø1.7 pegs reach ~3.05 and pins ~2.9;
  both are scaled off the front view.
- **PCB layout = MX pins** (the drawing shows it rotated 180°): centre Ø5.00, pegs Ø1.70 at ±5.08, pins Ø1.50
  at the MX positions. So it takes **MX-pattern hotswap sockets** (Gateron KS-2P02B01-01 / Kailh CPG151101S11).
  Keebio confirms the LP 3.0 = MX pinout plus a larger centre hole.
- Footprint `footprints/custom/switch_mx_ks33g.js` is ceoloide `switch_mx` with `center_hole_diameter: 5.0`
  (NPTH), pegs 1.7, and exclude-from-BOM/pos (so the PCBWay BOM matches the main board).
- `config.yaml`: the second `pcbs:` entry reuses every shared footprint through YAML anchors (`&fp_*` / `*fp_*`).
  Regenerating `not_about_money` from it gives the committed unrouted board byte for byte (except the date).
- **Socket rotations** were picked by DRC-sweeping all four on the unrouted board:
  - 1u: 180 (socket toward the front, clear of the diode at +7.1 and of RST1).
  - c2_r1/c2_r2 (under the nano): 270 is the only rotation that clears the kept nano pins. The
    `omit_pins` set and the pin map are unchanged, so the **firmware is the same**. Their diodes are shifted to
    x +7.9 (`diodes_mcu`) for body room.
  - "0" key: 180. Tall keys: 90.
- **MX socket body is an estimate** (no drawing found; Kailh's PDF has an expired cert): `build_case.py ks33g`
  uses two blocks around the barrels plus the pad tabs, 1.85 tall. Under the nano it must stay below the USB shell, 1.72 below the PCB at `HEADER_GAP` 2.5: the 1.85 estimate is 0.13 into it (S18), see Open items.
- `build_case.py ks33g` → (2026-11-07, with the new part-vs-part check) S18 socket vs USB shell (Open items), otherwise clean since the JST move; same Z_REAR 8.10, battery spot and screws. The tray and plate
  geometry are identical to the KS-33 case (only array order differs), so **one case fits both boards**. It
  writes to `case/ks33g/`, which was deleted after the check; regenerate it when needed.
- Routed 2026-11-01: 0 unconnected, no errors (cosmetic lib/silk warnings only). 18 vias, ~1.93 m of track.
- **Stabilizers with KS-33G (checked 2026-11-01):**
  - x/y: identical to the KS-33 board. Each 2u switch is centred between its stab cutouts (cutout centre offset
    2.275 toward the bar), and the plate is the same.
  - Height: the margin is thin. gmsh test (STEP solids 1/2 = actuators, 3/5 = housings, 4 = wire; actuator
    translated down until `intersect` with its housing > 0): the actuator hits the housing floor **3.25 below
    its STEP pose** (top 4.05 above the plate top). The KS-33G stem rests 0.05 higher (6.45 vs 6.40 above the
    plate) and travels 3.2 ±0.2 vs 3.0, so the stab has ~0.05 spare vs ~0.25 with the KS-33. A 3.4 switch could
    let the 2u ends stop ~0.15 early.
  - Unresolved: where the keycap holds the actuator at rest (drawing free height 7.70, STEP 7.30). The actuator
    rests on the wire arm, 0.08 above it.
  - A rigid rotation of the wire about its bar (y -7.975, z 3.825 in the STEP frame) overlaps the housing even at
    rest, so that model can't judge wire travel.
  - → **test-fit one 2u key** before buying a full set.

## Controller pin constraints (important)

An upright nice!nano can't clear the hotswap pads anywhere inside the current outline. The pin rows are
15.24mm apart, but the free gaps between switch columns are only about 2mm and the diodes sit in them.
Instead, `footprints/custom/mcu_nice_nano_sparse.js` (a copy of the ceoloide footprint plus an
`omit_pins` param) leaves out the unused pins that would overlap switch pads:
`P21,P20,P10,P2,P3,P9,VCC,#4`.
- `#N` omits a pad by number. This is needed for one GND pin, since several pins share the GND name. Pad 4
  is a GND and other GND pins remain. VCC (3.3V out) is unused.
- Matrix mapping, which ZMK must match:
  - Columns C1–C4 = P19, P18, P15, P14
  - R1 = P16
  - R2–R6 = P4, P5, P6, P7, P8
  - P0 drives the low-battery LED (active high). P1 is the only free spare.
- **Moving the MCU:** re-check that every pin it uses still clears the switch and diode pads by at least 0.2mm.
  Load the board with pcbnew and measure distance from each MCU pad to every other pad.
- **Header pins under switches (found 2026-11-07):** 7 kept pins of the nano's x 113.82 row come up through
  the PCB top *inside* a switch's 14×14 body (switch-local x -5.18): pads 14–16 (R1, C4, C3) under the
  c2_r2 switch (119,-24), pad 17 (C2) 0.33 into its edge, and pads 22–24 (RST, GND, RAW) under c2_r1 (119,-5).
  S9/S10 on the KS-33 board, S17/S18 on KS-33G. The KS-33 drawing shows a closed lower housing seated flat on
  the PCB, so these pins **must be cut flush** (README says so). Their plate pockets are moot (they're in the
  switch hole). `build_case.py` doesn't model pin tips above the PCB, so its collision report can't see this.
  RST1's empty Ø0.75 boss hole under c3_r1 is harmless.
- **Assembly:** use single header pins at the kept positions only. The controller sits over the hotswap
  sockets on the back, so it needs header spacing taller than about 1.8mm.
  - **Socketing (female/male headers), checked 2026-11-04:** the kept pins form a 3-pin run (USB end) and a
    5-pin run on each side. Use 3- and 5-pin segments: a full 12-pin strip's plastic would land on S10's
    socket body (left row) and S16's solder tab (right row). The 1.0 drills take normal header tails.
    The case (`HEADER_GAP`, now 2.5) is unchanged up to a 3.0 board-to-board gap. Above that it grows 1:1
    (3.5 → +0.5, 5.0 → +2.0, 8.5-tall female + 2.5 male spacer = 11 → +8.0), with no collisions; set
    `HEADER_GAP` to the real seated height and re-run `build_case.py`.
  - Candidate kit: Typeractive "Machine Sockets and Pins" (2× 12-pin Mill-Max 310-series machined socket
    strips + 26 loose Mill-Max pins). The 310 insulator is ~2.79 tall (listed for another 310 strip), so
    the case should stay unchanged. Cut each strip into 3 + 5 pieces.

## Files

Cleaned up 2026-10-01: only the current Gateron design is in the working tree. **Earlier iterations live in
git history.** Commit `c19e498` has `output_gateron/`, `output_toplayout/`, `output_keygap/`, `output_led/`,
the original choc output, every `config.yaml.*` backup (`config.yaml.bak` = the original choc config) and the
`case/build_case.py.pre-*` backups. Restore one with `git checkout c19e498 -- <path>`.
Untracked leftovers (KiCad backup zips, .kicad_prl) were moved to `../numpad-archive/`, outside the repo.

- `config.yaml`: the ergogen source of truth.
- `footprints/ceoloide/`: upstream ceoloide footprints. `footprints/custom/`: local modified footprints.
- `output/`: **current board** (was `output_stabfix/`).
  - Contents: the keygap + LED design with STEP-accurate stabilizer cutouts (bars inward), 2u sockets
    re-rotated with 1.6 outer pads, two screws moved, and the nano shifted 1.5 toward the edge (re-routed
    2026-10-04).
  - `pcbs/not_about_money.kicad_pcb` is **routed**: 0 unconnected, DRC errors none, only the cosmetic
    lib/silk warnings; report in `pcbs/drc.rpt`, preview `routed.svg`.
    - Re-routed 2026-11-07 for the tall-key diode move, and only partly. The old tracks were copied onto the
      regenerated board, minus nets R3/R5/c4_r3/c4_r5, which freerouting re-routed (keepout_dsn) in one
      clean pass. Scripts for this (`carry_tracks.py`, `cmp_boards.py`) were scratch-only; the recipe: for
      each old track, `new.FindNet(name)`, copy it as `PCB_TRACK`/`PCB_VIA`, lock it.
    - `pcbs/numpad_ks33g.unrouted.kicad_pcb` was re-saved by KiCad at some point, so compare it to fresh
      ergogen output with pcbnew (footprints/nets), not with a text diff.
  - `pcbs/not_about_money.unrouted.kicad_pcb` is the raw ergogen output. MCU pins clear other pads by ≥1.51.
  - `pcbs/numpad_ks33g.kicad_pcb` (routed) / `.unrouted.kicad_pcb`, `pcbs/drc_ks33g.rpt`, `routed_ks33g.svg`:
    the KS-33G variant (see its section). ergogen now emits both boards.
  - **Never run `ergogen -o output --clean`**: it empties the folder, wiping the routing (and anything else
    in `output/`). Generate into a scratch dir and copy `pcbs/ outlines/ cases/` over.
  - `case/build_case.py` reads `output/pcbs/not_about_money.kicad_pcb`.
- `kicad/`: the user's KiCad project (moved from `output/numpad/` on 2026-10-02, so ergogen can't wipe it).
  - `numpad.kicad_pcb` is a copy of the routed board. DRC is clean under the project's own rules (edge
    clearance 0.2): 0 violations, 0 unconnected.
  - `numpad_ks33g.kicad_pro/.kicad_pcb/.kicad_sch`: the KS-33G variant as a second project in the same folder
    (shares `3d/`). `export_all.sh numpad_ks33g` writes `fab_ks33g/`, `numpad_ks33g.kicad_pcb.zip`,
    `gerber_render_ks33g_*.png`, `drc_ks33g.rpt`.
  - **`scripts/export_all.sh [board]` regenerates every fab output** from `numpad.kicad_pcb` (run it after any board change):
    - `fab/`: gerbers (`--subtract-soldermask`, 9 layers), drill + map, `drc-report.txt`, `numpad-gerbers.zip`.
    - `numpad.kicad_pcb.zip`: the **PCBWay order package** in the PCBWay plugin's format: `.gbr` gerbers incl.
      User_Comments, separate PTH/NPTH Excellon (inch, decimal, absolute), IPC-D-356 netlist (needs KiCad 10's
      kicad-cli), `PCBWay_bom.csv`/`PCBWay_positions.csv` (`scripts/pcbway_bom.py`; it honours the footprints'
      exclude-from-BOM/pos flags, so the nano and switches are left out).
    - `gerber_render_top/bottom.png` (`scripts/render.py`): flat 4-colour 20 px/mm renders, both seen from the top
      (copper, then silk, then mask openings, then outline). README shows the top one.
    - Verified 2026-10-04: run on the old board, both recipes reproduce the 2026-10-01 exports exactly except
      timestamps (and KiCad 8 adds `FMAT,2` to the drill files); the renders match to 1-px edge rounding.
  - `3d/nice_nano_v2.step`: the user's nice!nano v2 CAD model, referenced by the MCU footprint as
    `${KIPRJMOD}/3d/nice_nano_v2.step` (so it only resolves next to a `.kicad_pro`). Footprint params in
    `config.yaml`: rotate `[0,0,-90]`, offset `[0,0.11,2.45]`. For a B-side footprint KiCad keeps the model's x/y
    and flips z, and drops it 0.05 extra; KiCad's +90 turned the USB the wrong way. Verified by
    `kicad-cli pcb export step` + parsing: USB mouth at KiCad y -5.697, nano board 2.5..3.9 below the PCB,
    model pins on the footprint pads.
  - Old choc/backup leftovers were pruned (in git history at `c19e498`/`70bfd2c`; untracked KiCad backup
    zips are in `../numpad-archive/`).
- `case/`: case build (`build_case.py`, generated jscad/STL, `viewer.html`, `battery_fit.py`, `board.html` +
  `board.svg`).
- `README.md` (build + assembly instructions), `SHOPPING_LIST.md` (BOM).

## Ergogen gotchas

- Custom footprints only load when the ergogen input is a **directory** (config.yaml + footprints/),
  not a plain yaml file. Copy both into a scratch dir, then run `ergogen <dir> -o output_xxx --clean`
  (global ergogen v4.1.0).
- Matrix nets:
  - Columns use `columns.cN.key.column_net`.
  - Rows use `rows.rN.row_net` directly under the row, NOT under `key:`.
- Ergogen y points up, KiCad y points down. `adjust.shift` is applied before `adjust.rotate`.
- nice!nano pads are through-hole (copper on both faces). Putting it on the other side does NOT avoid
  pad collisions.
- Edge-mounted side switches need copper-to-edge clearance set to 0.2mm.
- `where` filters: a top-level array is OR, and a nested array is AND. `-name` negates. Example:
  `where: [[/key/, -matrix_c1_r6]]`.
- Ergogen renumbers designators by placement order, so S-numbers shift when footprint entries change.

## Routing + DRC workflow

Ergogen output is unrouted.
1. Export DSN: `pcbnew.ExportSpecctraDSN(board, "x.dsn")`, using
   `"C:/Program Files/KiCad/8.0/bin/python.exe"`.
2. Route: `java -jar freerouting-1.4.5.jar -de x.dsn -do x.ses -mp 30`. Only Java 15 is installed,
   so newer freerouting won't run. The jar isn't kept: download
   `https://github.com/freerouting/freerouting/releases/download/v1.4.5/freerouting-1.4.5.jar` (~4MB).
   - Freerouting 1.4.5 doesn't apply edge clearance to the stab-cutout keepouts, and the first pass of
     the stabfix board left a short, a clearance error and an edge hit (nets R1/R4/R5). Deleting those nets'
     tracks, re-exporting the DSN (the remaining tracks stay fixed) and routing again fixed it.
   - It also ignores **no-net pads**: on the nano-shift board it ran RAW over a PWR1 mounting pad (a short).
     Same fix: delete RAW's tracks, lock the rest, re-export and route again.
   - **Better (2026-11-01, KS-33G board, whose Ø5 centre holes are NPTH):** export the DSN with
     `kicad/scripts/keepout_dsn.py` (rule-area keepouts over every no-net pad + 0.3), route, and import the .ses
     into the board *without* keepouts. If DRC still shows shorts or clearance errors (freerouting also clips real
     pads now and then), run `kicad/scripts/strip_bad_nets.py board drc.rpt stripped`, then keepout_dsn → route →
     import → DRC again. Two passes converged. Unlock the tracks at the end.
3. Import the session (`pcbnew.ImportSpecctraSES(board, "x.ses")`), set
   `GetDesignSettings().m_CopperEdgeClearance = FromMM(0.2)`, then save.
4. DRC: `kicad-cli pcb drc --severity-error --severity-warning -o x.rpt board.kicad_pcb`.
   The `lib_footprint_issues` and silkscreen warnings are cosmetic and expected.
   If freerouting leaves a clearance error, delete that net's tracks and re-run freerouting on that net only.
5. Preview: `kicad-cli pcb export svg --layers "B.Cu,F.Cu,B.SilkS,Edge.Cuts" --exclude-drawing-sheet --page-size-mode 2`.

## Case design & 3D preview (handoff for the case instance)

Ergogen emits cases as **JSCAD v1** files (`output_*/cases/*.jscad`), geometry in the **ergogen frame**.

- **Coordinate frame:** `ergogen_x = kicad_x`, `ergogen_y = -kicad_y`. **Rear (controller end) = +y.**
  Board centre `(128.5, -52.5)`. Current PCB = 76.5 × 114.5, cavity 77.0 × 115.0, shell 79.4 × 117.4.
  `build_case.py` derives all of these from the board outline.
- **Screw / standoff centres (ergogen frame, M2 = radius 1.1):**
  `(109.5,-33.5) (147.5,-14.5) (128.5,-52.5) (147.5,-71.5) (128.5,-90.5)`. The last two were moved off the
  stab bars. `build_case.py` reads them from the board.
- **Rendering jscad → STL (no GUI):** `npm install --prefix <scratch> @jscad/cli@1`, then
  `<scratch>/node_modules/.bin/openjscad in.jscad -o out.stl`. The **modern @jscad/cli v2 cannot run
  v1 jscad**, so you must use v1. Users can also drag a `.jscad` onto https://openjscad.xyz.
- **Case build:** `case/build_case.py` (the `BOARD` path at the top points to `output/pcbs`) is the source of
  truth. Run it with KiCad's python. It writes:
  - `case_bottom.jscad`: the tray.
  - `case_plate.jscad`: the plate.
  - `assembly.json`: the PCB + part boxes, including keycaps and stab housings.
  It also prints the stack-up and a **collision report** that checks:
  - parts vs standoffs and corner ledges;
  - parts in the plate gap vs the spacers and rim.
  Then render both jscad files with `@jscad/cli@1`. **Don't hand-edit the .jscad files.**
- **Geometry:** flat floor (1.0). PCB **tilted 2.37° (rear up), parallel to the sloped top edge**, pivoting
  about the PCB rear edge. `Z_REAR` is auto-computed so the lowest part clears the floor by 0.5. That gives
  PCB underside z = 8.1 at the rear and 3.37 at the front. Wall tops end flush with the plate top
  (rear 12.26, front 7.40).
- **Supports:** each screw pillar gets its own height, cut by the tilted PCB-underside plane. There are also
  L-shaped **corner ledges** (1.6 wide, 10mm arms). Supports are intersected with the cavity, so they
  never poke through the walls.
- **Plate vs board verified 2026-11-07** (both boards): render `case_plate.jscad`, slice the STL (trimesh
  `mesh_plane` + shapely, installed with `pip --target` in a scratch dir) and compare with a pcbnew dump. All 21
  switch holes are exactly ±7.00 on their footprints; stab wings and notches are on the bar side, as on the
  PCB, with housings 0.30 inside the PCB cutouts; screw holes are r 1.10, offset 0.000; every non-switch
  THT pad sits in a closed pocket with 0.50 margin; the LED hole is centred. Committed STLs = fresh renders.
- **Plate:** 1.2mm, top **2.5mm** above the PCB top (the KS-33 flange height; was 2.2 until 2026-10-05,
  which would have held every switch 0.3 off the PCB). It is inset inside the walls (0.2 per side).
  - Cutouts: 14×14 switch holes; Gateron LP stab cutouts per Gateron's suggested mounting (wings 6.0×12.5
    offset 0.595 toward the bar, 1.7×1.15 notch on the bar end, 2.5 neck at y -1.39; see Stabilizers). Each
    stab is rotated so its bar points inward (`stabs` rot 180 for the "0" key, 270 for the tall keys).
  - M2 holes. THT pins poking up through the PCB (nano headers, JST, reset/power pegs) get **blind pockets
    from below**: pad + 0.5, 0.6 deep, leaving a 0.6 skin, so the plate top stays closed. The user wants the
    components covered, not open holes. That leaves 1.9 above the PCB top for pins, so trim headers to ~1.4.
- **Switch:** Gateron KS-33 (spec gateron.com/u_file/2311/10/file/GATERONKS-33LowProfile20BrownSwitch
  BlackBottomHousingKS-33E10B055NN-Y24.pdf).
  - Re-read 2026-10-05 from the drawing on the PDF's last page (render it with pymupdf; the user's
    seller image of the same drawing lacks the front view). Heights from the switch's seat on the PCB top:
    - Plate cutout 14.00 (+0.05/-0.02), plate 1.20. **Flange underside (plate top) 2.50 up**, so the plate
      underside is 1.30 above the PCB top. (The old "5.75 to the stem top" was a misread: 5.75 runs from the
      flange underside *down* to the centre-post tip.)
    - 14.7 flange, 13.75 upper housing with its top at 5.85; stem top at 8.90 (12.15 overall − 3.25 post).
    - Below the seat: Ø5.05 centre post 3.25 (1.65 past our 1.6 PCB, modelled as `_post`), pins 2.60.
    - Travel 3.0 ±0.2, pre-travel 1.7 ±0.4.
    - Confirmed 2026-10-05 by the user's Banana/Yellow LP 2.0 spec (`Downloads/GATERONKS-33LowProfile20Banana
      Switch-KS-33-014KS-33Y10B060NN-D137.pdf`, drawing on its last page, vector with no text layer). Its body
      drawing is identical to the Brown one, and its front view dimensions **12.15 from stem top to post tip**
      directly (stem top = 12.15 − 5.75 + 2.50 = 8.90 above the seat). Only the force differs (60 ±15 gf).
      Gateron's PCB layout there asks for a **Ø5.25** centre hole and Ø3.00 socket holes; ours drills Ø5.1
      (plated) — open question for the user.
  - **Screws go in from the top:** M2 countersunk (bevel-head) self-tapping screws. The user chose this
    because it's stronger: the thread grips the pillar, not 1.5mm of plate. The underside of the case shows
    **no holes**.
    - Path: a 90° countersink in the plate top (r 2.0 → 1.1), so the head sits flush under the keycaps.
      Then r=1.1 clearance through the plate boss and PCB, then an **r=0.8 pilot down the full pillar**,
      cut flat at the floor top (world z = `FLOOR_T` = 1.0; user, 2026-10-04), so the 1.0 floor stays solid.
      Screw choice still keeps the tip ≥ `PILOT_EXTRA` (0.5) above the pilot bottom.
    - Every hole is square to the **tilted** board (the pilot is built in the board frame and passed
      through `T()`), so the screw axis matches the plate.
    - `build_case.py` picks the longest standard length per pillar and prints it: currently M2x8 at
      (109.5,-33.5), (147.5,-14.5) and (128.5,-52.5); M2x6 at (147.5,-71.5) and (128.5,-90.5), where the
      pillars are 4.1–4.9 tall, giving 1.9mm of thread (3.9 on the M2x8s).
  - **Underneath:** a 1.2-wide edge rim and r=2.15 spacer bosses at the screws. Both fill the 1.3 gap down
    to the PCB top, so no loose spacers are needed. Print the plate upside down.
- **Stabs in the assembly model** (from the STEP): housing, flange and bar boxes, checked against the spacer
  bosses, rim, pillars and ledges. Every stab part that reaches into the PCB was verified to fall inside the
  PCB cutouts (point-in-polygon test against `assembly.json` `poly_holes`).
- **Rear-wall windows:** closed on all four sides (the user does NOT want open-topped slots). Each is part
  outline + 0.4 per side, in the board frame. USB-C 8.94×3.16 (`USB_GAP` 0.25 per side, from the CAD model) at the back of a **cable-head scoop**
  (`USB_SCOOP` 12.5×6.5 r1.5, user's size 2026-10-04). The user does NOT want a through-hole: the scoop is a
  recess from the outer face down to a back wall **flush with the USB mouth**. If the mouth is behind the
  inner wall face, a **collar** (`COLLAR_*`, scoop + 1.2 margin, from the floor to 0.2 below the PCB) is added
  inside the cavity to make that back wall; with the nano shifted (below) the mouth is inside the wall, so the
  collar is skipped and the recess is only ~0.5 deep. The shell slides into its window rear-first (like the lever).
- **Nano shift (2026-10-04, done):** the nano is 1.5 closer to the top edge (KiCad y 13.25 → 11.75): its edge is
  flush with the PCB edge, the USB mouth 0.96 past it (0.49 behind the outer wall face, 0.26 nano-to-inner-wall).
  `build_case.py` has a `NANO_SHIFT` preview offset for trying moves in the case before the PCB; keep it **0**.
  Reset
  plunger; power lever with ±1.65 travel (no nail scoop: the lever pokes ~0.53 past the outer wall). The
  user is fine angling the PCB in past the lever. The reset plunger stays ~1 mm inside the wall (paperclip).
- **Part dimensions and where they came from** (2026-10-01):
  - From datasheets/models:
    - Gateron KS-33 switch: spec PDF.
    - KS-57 stabilizer: STEP model.
    - **Panasonic EVQ-PU family** (reset): 4.7×3.5 body, height 1.65 +0.3, modelled at 1.95. Push plate 2.6
      wide, sticks out 1.0, 0.3 travel. The BOM says **EVQ-PUA02K** (easier to find than PUC02K). PUA has no
      pegs, so the board's two Ø0.75 boss holes stay empty. Not EVQ-PUD02K (3.2 deep). A generic 2×4 side-push
      the user found was rejected: different pads.
    - **Power: MSK-12C02-style side slide, H = 2.5 variant** (2026-10-02, replaces the Alps SSSS811101, whose
      1.5 lever ended ~0.5 inside the outer wall). Same land pattern as the ceoloide `power_switch_smd_side`
      footprint (pads mirrored on B), so no PCB change. 6.65×2.7×1.4 body. Actuator 1.3 wide, 1.1 thick
      (centre 0.65 off the board), sticks out **2.5 from the body face**, **1.5 travel** (the window covers the
      2.8 sweep + 0.4 per side). Lever tip ends 0.53 past the outer rear wall. The 1.5/2.0 variants are too short.
    - **JST PH S2B-PH-K-S**: 5.9×7.6×4.8. Its pins are 3.4 long, so they poke **1.8 through the PCB top**; the
      plate pocket allows 1.9, so they just fit, but **trim the JST pins** anyway. The mated PHR-2 plug reaches 9.6 from the back
      of the header; the model adds a plug + 3mm wire-bend keep-out on the +x (open) side.
    - **nice!nano v2: from its CAD model** (`C:/Users/Nuggets/AppData/Local/Temp/nice!nano v2.step`, user-supplied
      2026-10-04; parse with the same entity-walk as the stab STEP plus the NAUO/ITEM_DEFINED_TRANSFORMATION
      assembly transforms, sampling circle arcs). PCB 17.8×33.2×**1.4**; parts ≤1.1 tall. USB-C is a GCT
      USB4520-03-0-A mid-mount: shell 8.94×3.16, sticks **0.783 out of the bare (our-PCB-facing) face** and 0.977
      past the parts face; mouth 4.747 past the first header pin row (0.96 past the nano edge), centred ±0.075.
      Our mount is components-away (`reverse_mount: false`), so the shell sits 1.72..4.88 below our PCB underside.
      vs the old guess this moved the USB window 0.77 toward the PCB and the mouth 0.59 inward.
      **Nano LEDs** (from the STEP, 2026-10-04): two 0603s on the parts face, one on each side of the USB shell,
      7.4..9.0 in from the nano's USB edge at ±5.1..5.9 off its centreline. On our board that is about KiCad
      x 116 and 127, y 2.9..4.5. They face **down at the case floor** (~2.1 air gap) about 9 from the outer rear
      wall, directly behind the edges of the USB scoop. One is the hardware charge LED and the other is the
      blue user LED on P0.15. Discussed as a light-pipe alternative to `battery_led`; not adopted.
    - Rejected nano models: `bstiq/nice-nano-kicad` `sparkfun_pro_micro.x3d` (Pro Micro / micro-USB stand-in);
      `Downloads/nice nano prototype.stl` (220-triangle block model, 8.0-wide shell, wrong).
    - **Gateron LP hotswap socket (KS-2P02B01-02): from its drawing** (user-supplied 2026-10-05, a seller
      image `Desktop/S901b...q.avif`; no part number printed, but the hole pattern is the LP one). Body
      **1.85±0.05** tall (3.00 incl. the Ø2.90 barrels that go into the Ø3 holes), 11.85 long, 5.40 / 4.35
      wide. Holes 7.00 apart, 2.42 in from each body end; PCB layout = holes at (∓4.4, 4.7) and (±2.6, 5.75),
      Ø5.1 centre, i.e. **exactly the ceoloide B-side footprint**. Terminals 1.74 wide, **15.1 tip to tip**
      (1.63 past each body end), so in footprint x they end at **-8.45 / +6.65**. That is 1.1 shorter per end
      than the official footprint's B.Fab rects (-9.55 / +7.75) used for `SOCKET_TABS`.
      (The MX-profile sibling KS-2P02B01-01 has 6.35/2.54 holes and does not fit the KS-33 footprint.)
  - Still estimated:
    - nice!nano header gap 2.5 (standard spacer, but solder seating varies); keycap height.
- **Battery:** `case/battery_fit.py [floor_pocket_depth]` searches where LiPo pouch cells fit under the
  tilted PCB, using assembly.json. Re-run it after any change.
  - Results (2026-10-05, no pocket): 301230 (30×12×3, ~110mAh, nice!nano's recommended cell) and 401230
    (×4, ~150mAh) fit at **x 130..160, y -10..2**: 301230 with 1.2 spare, 401230 with 0.2.
  - 302030 fits at x 92..112, y -28..2 with 0.5 spare (tight). Anything wider doesn't fit.
  - **Chosen: 301230** (user, 2026-10-01). `build_case.py` (`BATTERY`, `BATT_*`) searches for the
    best-clearance spot and cuts a **0.5-deep floor pocket** (cell + 0.5 per side), plus a 4×6 lead notch on
    the end facing the JST.
    - Current spot (since 2026-10-05): **x 130.5..160.5, y -11..1**, lying across the rear right, under the
      top switch row, 1.72 spare under the S16/S18 sockets. The lead runs about 31mm (since the JST move) from its x 130.5 end to
      the JST. A 301230's lead is usually 40–50mm.
    - The previous spot (x 98.5..110.5, y -27.5..2.5, left of the nano) still fits with 1.36 spare. It dropped
      out when the switch centre posts were added to the model (S4's post is lowest there).
    - The battery is drawn in the viewer as a world-frame box (`assembly.json` `world_boxes`).
- **Socket model:** the user supplied the official Gateron LP socket KiCad footprint
  ("Gateron_Low_Profile_Socket", KS-2P02B01-02). `SOCKET_BODY`/`SOCKET_TABS` in `build_case.py` come from
  its B.SilkS outline and B.Fab tab rects. Its holes match the ceoloide footprint exactly. Its solder tabs
  reach 0.2 further out than the ceoloide pads (x -9.55 / +7.75).
  - With these real tabs, the PCB underside sits at z 8.1 at the rear and 3.37 at the front.
  - **2u keys (S19/S20/S21): the user hand-sands the pad-1 solder tab** (the one pointing at the stabilizer
    cutout) **1.1mm shorter**, leaving 1.45mm of tab.
    - **Probably unnecessary (2026-10-05):** the socket drawing puts the real tab tip at 8.45, the same as
      the trimmed value, so the 1.1 is likely the fab rect's pad margin, not metal. Caliper a real socket
      (tabs 15.1 tip to tip → skip the sanding) before dropping the step from the README.
    - Untrimmed, that tab hangs over the stab cutout and hits the housing (~0.5mm), and no socket rotation
      avoids it.
    - Trimmed, it ends 8.45 from the switch centre, 0.3 inside the cutout edge (8.75) and clear of the
      housing (9.07). It still covers 1.35mm of its 1.6-wide pad.
    - Modelled via `SOCKET_TAB0_TRIM_2U`; the collision report is clean.
- **Viewer:** `case/viewer.html` (three.js) shows case, plate, PCB (with stab holes), parts and keycaps,
  with toggles, see-through, a y-slice and side/rear views. Serve it with `python -m http.server 8765` from `case/`.

## Repo / GitHub

- Git repo initialised 2026-10-01 on branch `main`. Remote `origin` = https://github.com/lllNuggetslll/Numpad-Build-1
  (public); `main` was pushed 2026-10-01. `README.md` has the build and assembly
  instructions. `SHOPPING_LIST.md` is the BOM. `.gitignore` skips KiCad lock/autosave/cache files, logs,
  node_modules and freerouting files.
- Keep README.md, SHOPPING_LIST.md and this file in sync when parts, screw lengths or the battery change.

## Fabrication (sending to a PCB house)

- No schematic needed — `config.yaml` is the netlist source of truth (verified: 0 unconnected, DRC clean).
- Bare board, 2-layer, 1.6mm. Export: `kicad-cli pcb export gerbers --output fab/ board.kicad_pcb` and
  `kicad-cli pcb export drill --output fab/ board.kicad_pcb`, then zip. Design values (0.2mm track on
  every net, power included; 0.2mm clearance, 0.6/0.3 via) are within any fab's limits.
- Power path (measured 2026-10-04, JST then at 128.5,32.5): JST → BAT_P ~52mm, 1 via → power switch → RAW
  ~39mm → nano pin 24. About 0.22 Ω in total at 1oz, so roughly 22 mV drop at the nano's 100 mA charge
  current. The 2026-11-07 JST move added ~4mm to BAT_P (negligible).

## Open items

- If the board changes again, re-route it, copy it into `kicad/numpad.kicad_pcb` and run `kicad/scripts/export_all.sh`.
- **KS-33G: S18's MX socket overlaps the nano's USB shell by 0.13** (shell 1.72 below the PCB at
  `HEADER_GAP` 2.5, socket est. 1.85), reported by `build_case.py ks33g`'s part-vs-part check. Raise
  `HEADER_GAP` to ≥ 2.7 (socketed headers do that) or confirm the socket height.

## JST battery connector move (2026-11-07, done)

- **The old spot collided on every earlier revision, including the user's fabricated boards.** JST1 (side-entry
  S2B-PH-K-S, rot 90, at KiCad 128.5,32.5; body x 127.1..134.8 y 29.5..35.5 from its B.Fab = JST's 5.9 width)
  lay on S15's socket (c3_r2, KS-33 board) by 1.37 in y over x 131..134.8, plus S15's pad-1 tab. On KS-33G it
  hit S13's MX socket.
  - Bodge for built boards (in README): leave the JST off and solder the battery leads into JST1's holes
    (pad 1 GND at y 31.5, pad 2 BAT_P at y 33.5).
- **Now at KiCad (128.5, 35.5)** (config shift y `- 2` instead of `+ 1`), pads GND (128.5,34.5), BAT_P
  (128.5,36.5), on both boards. Found by a grid search over both boards' part boxes, case posts/ledges, the
  battery, plate-pocket vs switch holes and pad clearance. It is the only clear spot near the old one: 0.68 to the
  nearest part, floor gap 0.52. Any further forward raises `Z_REAR` (the body bottom would hit the floor
  clearance). The only other clear spots were at the left edge (x ~110, y -1 or 16).
- Re-routed by hand (pcbnew script, scratch only): old tracks copied, the 5 stub segments to the old pads
  dropped, new F.Cu GND/BAT_P stubs (KS-33G: BAT_P on B.Cu along x 130.08). DRC on both boards: 0 unconnected,
  cosmetic warnings only. Case unchanged except the plate's pin pockets; battery spot, Z_REAR and screws are the same.
- `build_case.py` has a **part-vs-part check** since then (boxes of different parts must not overlap; pieces
  of one part may).

- KS-33G board: measure the MX hotswap sockets (body height, outline) before ordering; the case model's socket
  is an estimate and must stay under the USB shell (1.72 below the PCB at `HEADER_GAP` 2.5), or raise `HEADER_GAP`.
- Switch centre hole (KS-33 board): Gateron's KS-33 layout says Ø5.25; the footprint drills a plated Ø5.1 for a Ø5.05
  post, which may come out too tight. Enlarging the drill (pad 5.6 unchanged) needs the user's OK, then a
  DRC + `export_all.sh`.
- Test-print the rear wall with the user's USB-C cable: cable heads bigger than 12.5×6.5 won't fit the scoop.
- KS-33G: test-fit one 2u key (switch + KS-57 stab + keycap). Both ends must bottom out like the middle; the
  stab's travel is only ~0.05 more than the switch's nominal 3.2.
- Before committing to the plate, test-print one stab cutout (now Gateron's suggested mounting, checked against
  the STEP; FDM holes print small, and the latch catch is only ~0.05).
- Assembly reminder: sand 1.1mm off the stab-facing solder tab of the three 2u sockets before soldering
  (resolved by the user's choice; see Case → Socket model).
- Case: verify part heights against real parts (the nano header gap is still an estimate; socket height is confirmed at 1.85 by its drawing).
- ZMK has no built-in low-battery LED. It needs a module or ~50 lines of custom code that blinks P0
  (nRF P0.08) when the battery is low. Blink only; leaving it on drains the battery.
- The ZMK firmware pin mapping needs updating to match the remap above. (The VCC pin is no longer
  connected, so don't rely on it.)
