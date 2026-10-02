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
  - nice!nano: USB at the top edge, left of center (KiCad x=121.44, y=13.25, rotation 0).
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
    - Housings 24.00 apart; 6.0 wide. Plate cutout 12.5 long, spanning y -6.5..+6.0 (the clip hooks catch the
      plate underside at -6.5). The 1.7 notch is on the **+y end, away from the bar**.
    - Housing below the plate: x ±2.93, **y -9.70..+5.13**, down to 4.45 below the plate top.
    - **Wire bar:** r 0.5 at y -7.975. Its centre sits 0.725 below the plate underside, so with our 1.0
      plate-PCB gap it hangs **0.225 into the PCB**.
  - **PCB cutout per 2u key** (`_stab_holes` → `_pcb_outline`):
    - Two housing holes 6.5×15.45, offset 2.275 toward the bar, joined by a 1.6-wide bar slot at 7.975.
    - **Bars point inward** (toward the board centre). Outward, the housing holes break the PCB edge and the
      slot would cut a strip loose.
  - **2u switch footprints:** separate `key_switch_0` (c1_r6, `rotate: 0`) and `key_switch_tall`
    (c4_r3/c4_r5, `rotate: 90`) entries, both with `outer_pad_width_*: 1.6`, so the socket pads clear the
    cutouts. The rotations were picked by DRC-testing all four; the cross stem doesn't care.
  - **Screws moved for the bars:** front-left → (128.5, 90.5) (`ref: matrix_c3_r6`, past the end of the "0"
    key's bar); front-right → (147.5, 71.5) (one row back). See the case section.
- **Low-battery LED (the one exception to "everything on B"):** `battery_led` is a 0603 LED on the
  **front** at the keycap-gap crossing "E" (KiCad 128.5, 71.5; between c2/c3 and r4/r5). The plate has a
  3.8×2.0 counterbore (blind pocket from below, 0.6 deep) over it, which leaves 1.6 of room, so any 0603
  LED up to ~1.4 tall fits. Planned part: Lite-On LTST-C191KRKT (red, 0.55). There is a Ø1.8 through hole
  in the middle (`LED_HOLE_R`, `LED_POCKET`). Its 1k resistor `battery_led_resistor` sits on B directly under
  it. Circuit: P0 → R → LED_A → LED → GND. Both use `footprints/custom/smd_0603.js`.
  - Other free crossings, each with ≥3.17mm to the nearest pad: (109.5,14.5), (147.5,33.5), (109.5,52.5),
    (109.5,71.5). (147.5,71.5) and (128.5,90.5) now hold screws. The other crossings hold screws, an MCU
    pin or the JST connector.
- Use hotswap switches (`ceoloide/switch_gateron_ks27_ks33`, `hotswap: true`, `solder: false`), not choc.
- Show the user a quick prototype image before a big layout change.
- The user has KiCad 8 (and 10) installed. Drive it through its bundled Python (`pcbnew`) and `kicad-cli`.

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
- **Assembly:** use single header pins at the kept positions only. The controller sits over the hotswap
  sockets on the back, so it needs header spacing taller than about 1.8mm.

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
    re-rotated with 1.6 outer pads, and two screws moved.
  - `pcbs/not_about_money.kicad_pcb` is **routed**: 0 unconnected, DRC errors none, only the cosmetic
    lib/silk warnings; report in `pcbs/drc.rpt`, preview `routed.svg`.
  - `pcbs/not_about_money.unrouted.kicad_pcb` is the raw ergogen output. MCU pins clear by ≥0.258.
  - **Never run `ergogen -o output --clean`**: it empties the folder, wiping the routing (and anything else
    in `output/`). Generate into a scratch dir and copy `pcbs/ outlines/ cases/` over.
  - `case/build_case.py` reads `output/pcbs/not_about_money.kicad_pcb`.
- `kicad/`: the user's KiCad project (moved from `output/numpad/` on 2026-10-02, so ergogen can't wipe it).
  - `numpad.kicad_pcb` is a copy of the routed board. DRC is clean under the project's own rules (edge
    clearance 0.2): 0 violations, 0 unconnected.
  - `fab/` holds the **current** gerbers + drill + `numpad-gerbers.zip`.
  - `numpad.kicad_pcb.zip` is a **PCBWay order package** (gerbers, drill, PCBWay BOM/netlist/positions),
    exported from the current board 2026-10-01 23:37, likely with PCBWay's KiCad plugin.
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
  PCB underside z = 8.0 at the rear and 3.27 at the front. Wall tops end flush with the plate top
  (rear 11.86, front 7.0).
- **Supports:** each screw pillar gets its own height, cut by the tilted PCB-underside plane. There are also
  L-shaped **corner ledges** (1.6 wide, 10mm arms). Supports are intersected with the cavity, so they
  never poke through the walls.
- **Plate:** 1.2mm, top 2.2mm above the PCB top. It is inset inside the walls (0.2 per side).
  - Cutouts: 14×14 switch holes; Gateron LP stab cutouts (wings 6.0×12.5 offset 0.25 toward the bar,
    1.7×1.0 notch on the side away from the bar, 2.0 neck). Each stab is rotated so its bar points
    inward (`stabs` rot 180 for the "0" key, 270 for the tall keys). The neck height comes from a
    not-to-scale drawing.
  - M2 holes. THT pins poking up through the PCB (nano headers, JST, reset/power pegs) get **blind pockets
    from below**: pad + 0.5, 0.6 deep, leaving a 0.6 skin, so the plate top stays closed. The user wants the
    components covered, not open holes. That leaves 1.6 above the PCB top for pins, so trim headers to ~1.4.
- **Switch:** Gateron KS-33 (spec gateron.com/u_file/2311/10/file/GATERONKS-33LowProfile20BrownSwitch
  BlackBottomHousingKS-33E10B055NN-Y24.pdf).
  - Plate cutout 14.00, plate 1.20, plate underside 1.00 above the PCB top.
  - 14.7 flange, 13.75 upper housing, 5.75 from the PCB top to the stem top; pins 2.60 below the PCB top;
    3.0 total travel.
  - **Screws go in from the top:** M2 countersunk (bevel-head) self-tapping screws. The user chose this
    because it's stronger: the thread grips the pillar, not 1.5mm of plate. The underside of the case shows
    **no holes**.
    - Path: a 90° countersink in the plate top (r 2.0 → 1.1), so the head sits flush under the keycaps.
      Then r=1.1 clearance through the plate boss and PCB, then a **blind r=0.8 pilot in the pillar**,
      stopping 0.8 above the floor bottom.
    - Every hole is square to the **tilted** board (the pilot is built in the board frame and passed
      through `T()`), so the screw axis matches the plate.
    - `build_case.py` picks the longest standard length per pillar and prints it: currently M2x8 at
      (109.5,-33.5), (147.5,-14.5) and (128.5,-52.5); M2x6 at (147.5,-71.5) and (128.5,-90.5), where the
      pillars are 4.1–4.9 tall, giving 2.2mm of thread.
  - **Underneath:** a 1.2-wide edge rim and r=2.15 spacer bosses at the screws. Both fill the 1.0 gap down
    to the PCB top, so no loose spacers are needed. Print the plate upside down.
- **Stabs in the assembly model** (from the STEP): housing, flange and bar boxes, checked against the spacer
  bosses, rim, pillars and ledges. Every stab part that reaches into the PCB was verified to fall inside the
  PCB cutouts (point-in-polygon test against `assembly.json` `poly_holes`).
- **Rear-wall windows:** closed on all four sides (the user does NOT want open-topped slots). Each is part
  outline + 0.4 per side, in the board frame. USB-C 8.94×3.26 + an outer overmold pocket 0.6 deep; reset
  plunger; power lever with ±1.65 travel + a nail scoop. The user is fine angling the PCB in past the lever.
- **Part dimensions and where they came from** (2026-10-01):
  - From datasheets/models:
    - Gateron KS-33 switch: spec PDF.
    - KS-57 stabilizer: STEP model.
    - **Panasonic EVQ-PUC02K** (reset): 4.7×3.5 body, height 1.65 +0.3, modelled at 1.95. Push plate 2.6
      wide, sticks out 1.0, 0.3 travel.
    - **Alps SSSS811101** (power): 6.7×2.6×1.4 body. Actuator 1.3 wide, 1.1 thick (centre 0.65 off the board),
      sticks out 1.5, **1.5 travel** (the window covers the 2.8 sweep + 0.4 per side).
    - **JST PH S2B-PH-K-S**: 5.9×7.6×4.8. Its pins are 3.4 long, so they poke **1.8 through the PCB top**, but
      the plate pocket only allows 1.6: **trim the JST pins**. The mated PHR-2 plug reaches 9.6 from the back
      of the header; the model adds a plug + 3mm wire-bend keep-out on the +x (open) side.
    - nice!nano: 3.2 total thickness with a mid-mount USB-C (nicekeyboards docs).
  - Still estimated:
    - Gateron LP hotswap socket (KS-2P02B01-**02**) height 1.85. Its spec PDF URL is dead (404).
      Supporting evidence: the user linked the MX-profile sibling KS-2P02B01-**01**
      (gateron.com/u_file/2506/10/file/GATERONUpgradeHot-swapPCB20Socket-KS-2P02B01-01-a.pdf). It is
      **1.85±0.05** tall, but it has the MX pin layout (6.35/2.54, Ø3.0 holes) and does **not** fit the KS-33
      footprint. The KS-33 needs the -02 low-profile socket.
    - nice!nano PCB 1.0 and header gap 2.5; keycap height.
- **Battery:** `case/battery_fit.py [floor_pocket_depth]` searches where LiPo pouch cells fit under the
  tilted PCB, using assembly.json. Re-run it after any change.
  - Results: 301230 (30×12×3, ~110mAh, nice!nano's recommended cell) and 401230 (×4, ~150mAh) fit at
    **x 130..142, y -26..4** (right of the nano, ending by the JST). 301230 has 1.1 spare; 401230 has 0.1,
    or 0.7 with a 0.6 floor pocket.
  - 302030 fits only with a pocket and 0.2 spare (too tight). Anything wider doesn't fit.
  - **Chosen: 301230** (user, 2026-10-01). `build_case.py` (`BATTERY`, `BATT_*`) searches for the
    best-clearance spot and cuts a **0.5-deep floor pocket** (cell + 0.5 per side), plus a 4×6 lead notch on
    the end facing the JST.
    - Current spot: x 98.5..110.5, y -27.5..2.5 (left of the nano), 1.72 spare under the S5 socket.
    - The lead runs about 27mm to the JST, passing under the nano. A 301230's lead is usually 40–50mm.
    - The battery is drawn in the viewer as a world-frame box (`assembly.json` `world_boxes`).
- **Socket model:** the user supplied the official Gateron LP socket KiCad footprint
  ("Gateron_Low_Profile_Socket", KS-2P02B01-02). `SOCKET_BODY`/`SOCKET_TABS` in `build_case.py` come from
  its B.SilkS outline and B.Fab tab rects. Its holes match the ceoloide footprint exactly. Its solder tabs
  reach 0.2 further out than the ceoloide pads (x -9.55 / +7.75).
  - With these real tabs, the PCB underside sits at z 8.1 at the rear and 3.37 at the front.
  - **2u keys (S19/S20/S21): the user hand-sands the pad-1 solder tab** (the one pointing at the stabilizer
    cutout) **1.1mm shorter**, leaving 1.45mm of tab.
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
  `kicad-cli pcb export drill --output fab/ board.kicad_pcb`, then zip. Design values (0.25mm track,
  0.2mm clearance, 0.6/0.3 via) are within any fab's limits.

## Open items

- If the board changes again, re-route it, copy it into `kicad/numpad.kicad_pcb` and re-export `kicad/fab/` (and the PCBWay zip).

- Before committing to the plate, test-print one stab cutout: the notch depth and neck size are estimates.
- Assembly reminder: sand 1.1mm off the stab-facing solder tab of the three 2u sockets before soldering
  (resolved by the user's choice; see Case → Socket model).
- Case: verify part heights against real parts (socket height and nano PCB/header gap are still estimates).
- ZMK has no built-in low-battery LED. It needs a module or ~50 lines of custom code that blinks P0
  (nRF P0.08) when the battery is low. Blink only; leaving it on drains the battery.
- The ZMK firmware pin mapping needs updating to match the remap above. (The VCC pin is no longer
  connected, so don't rely on it.)
