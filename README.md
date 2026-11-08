# Low-profile wireless numpad

A 21-key low-profile numpad: 4 columns × 6 rows, with three 2u keys ("0", "+", "Enter").

- **Controller:** nice!nano v2, running ZMK over Bluetooth.
- **Switches:** Gateron KS-33 low-profile switches in hotswap sockets. A second PCB variant takes the
  newer **KS-33G (Low Profile 3.0)** switches instead (see [KS-33G variant](#ks-33g-variant)).
- **Battery:** a 301230 LiPo with a low-battery LED.
- **Case:** a tilted 3D-printed case with a separate switch plate.

It's based on ceoloide's "not about money" ergogen design. The PCB is generated with
[ergogen](https://ergogen.xyz), routed with freerouting, and checked in KiCad 8. The case is generated
from the board itself, so the two always match.

![PCB top](kicad/gerber_render_top.png)

## Status

| Piece | State |
|---|---|
| PCB | Routed and DRC-clean. Gerbers are ready in `kicad/fab/numpad-gerbers.zip` (a PCBWay-ready package is `kicad/numpad.kicad_pcb.zip`). |
| PCB, KS-33G variant | Routed and DRC-clean: `kicad/fab_ks33g/numpad_ks33g-gerbers.zip`, PCBWay package `kicad/numpad_ks33g.kicad_pcb.zip`. |
| Case and plate | `case/case_bottom.stl`, `case/case_plate.stl` (the same case fits both boards) |
| Firmware | Not written yet. ZMK needs a board definition using the pin map below. |

Before printing the whole plate, **test-print one stabilizer cutout**. It follows Gateron's suggested mounting
drawing and was checked against the stabilizer's 3D model, but 3D-printed holes usually come out a little
small. The stabilizer should hook in at the wire end, then snap down at the other end and sit flat.

## Shopping list

See **[SHOPPING_LIST.md](SHOPPING_LIST.md)**.

## Repository layout

| Path | What it is |
|---|---|
| `config.yaml` | Ergogen source of truth for the PCB: layout, footprints, outline. |
| `footprints/ceoloide/` | Upstream ceoloide footprints. |
| `footprints/custom/` | Local footprints. `mcu_nice_nano_sparse.js` adds an `omit_pins` option; `smd_0603.js` is for the LED and resistor; `switch_mx_ks33g.js` is the KS-33G switch (MX sockets, Ø5.0 centre). |
| `output/` | **Current board.** `pcbs/not_about_money.kicad_pcb` is routed (DRC report `pcbs/drc.rpt`, preview `routed.svg`); `not_about_money.unrouted.kicad_pcb` is the raw ergogen output. |
| `kicad/` | KiCad project for the current board (with the project's 0.2 mm edge-clearance rule), `fab/` (gerbers + drill + zip), and the PCBWay package `numpad.kicad_pcb.zip`. The KS-33G variant is a second project in the same folder: `numpad_ks33g.kicad_pro`, `fab_ks33g/`, `numpad_ks33g.kicad_pcb.zip`. |
| `case/build_case.py` | Generates the case from the board: `case_bottom.jscad`, `case_plate.jscad`, `assembly.json`. |
| `case/viewer.html` | 3D viewer of the case, plate, PCB, parts, keycaps and battery. |
| `case/battery_fit.py` | Finds where LiPo cells fit under the tilted PCB. |
| Git history | Earlier design iterations (commit `c19e498` has every old `output_*` folder and config backup). |
| `CLAUDE.md` | Detailed design notes: coordinates, measurements, decisions, gotchas. |

## KS-33G variant

Gateron's **KS-33G** switches (Low Profile 3.0, e.g. Silent Red KS-33GJH10B045NW-X5B) look like the KS-33 from
the top: same 14.00 mm plate cutout, same 2.50 mm from the PCB to the plate top, same plate. Underneath they're
different. They use the **MX pin layout** (Ø1.5 pins), two Ø1.7 plastic pegs, and a **Ø5.0 centre post**, so
they need MX-style hotswap sockets and a different PCB. Only the switch footprints differ; everything else is the
same board.

| | KS-33 board (`numpad.kicad_pcb`) | KS-33G board (`numpad_ks33g.kicad_pcb`) |
|---|---|---|
| Switch | Gateron KS-33 (Low Profile 2.0) | Gateron KS-33G (Low Profile 3.0) |
| Hotswap socket | Gateron LP 2.0, KS-2P02B01-**02** | MX-pattern socket: Gateron KS-2P02B01-**01** or Kailh CPG151101S11 |
| Socket sanding on the 2u keys | yes (step 1 below) | no |
| Case, plate, stabilizers, nice!nano, firmware pin map | same | same |

- The two sockets under the nice!nano (the top two keys of column 2) are turned a different way from the
  others so they clear its pins. The diodes next to them sit 0.8 mm further right.
- **Test-fit one 2u key before buying a full set of switches.** Put a KS-33G, a KS-57 stabilizer and a 2u
  keycap together and press each end of the key. Both ends should bottom out as firmly as the middle. The
  stabilizers line up exactly as on the KS-33 board, but the KS-33G travels 3.2 mm (±0.2), and the stabilizer's
  actuator only has about 3.25 mm before it hits its housing. A long-travel switch could leave the ends of a 2u
  key stopping ~0.15 mm short.
- **Measure the MX sockets before you order the board.** The socket body height is an estimate (1.85 mm). It
  has to stay under ~2.3 mm, because two of the sockets sit under the nice!nano on its 2.5 mm headers.
- The KS-33G's centre post reaches 3.70 mm below its seat (0.45 mm more than the KS-33). The case check
  still finds no collisions, and the battery spot and screw lengths don't change.

## 1. Order the PCB

Upload `kicad/fab/numpad-gerbers.zip` to any PCB fab (for KS-33G switches: `kicad/fab_ks33g/numpad_ks33g-gerbers.zip`
and `kicad/numpad_ks33g.kicad_pcb.zip`). For PCBWay, `kicad/numpad.kicad_pcb.zip` already includes their BOM, netlist and positions files. Order a 2-layer, 1.6 mm, standard-spec board. The
design values (0.25 mm tracks, 0.2 mm clearance, 0.6/0.3 mm vias) are within every fab's limits. The three
stabilizer cutouts are part of the board outline.

## 2. Print the case

- **`case/case_bottom.stl`:** print as-is (floor down). It has a 0.5 mm battery pocket in the floor and three
  windows in the back wall: USB-C, reset, and the power-switch lever. The USB-C port sits at the back of a
  12.5 × 6.5 mm recess so a cable head can reach it; the recess's back wall is flush with the port.
- **`case/case_plate.stl`:** print **upside down** (plate top on the bed). The edge rim and the spacer posts
  around the screws are on its underside.
- **Settings:** PLA or PETG, 0.2 mm layers. No supports needed.

## 3. Assemble

The switches go on the front of the PCB. **Everything else** goes on the back (side B), except the
low-battery LED, which is on the front.

1. **Trim three sockets** (KS-33 board only; skip this on the KS-33G board). On the hotswap sockets for the three 2u keys ("0", "+", "Enter"), sand
   **1.1 mm off the tip of the solder tab that points at the stabilizer cutout**, leaving about 1.4–1.5 mm of
   tab. Without this, that tab hits the stabilizer housing. Dry-fit each socket to find the right tab, then
   clean and tin it.
2. **Back side SMD parts:** solder the 21 diodes (mind the cathode band), the 21 hotswap sockets, the reset
   button, the power switch, and the 1 kΩ resistor.
3. **Front side:** solder the 0603 LED. It sits under a hole in the plate between the keycaps.
4. **Battery connector:** solder the JST PH on the back, then **trim its pins flush** on the front. They're
   3.4 mm long and poke 1.8 mm through; the plate only leaves 1.9 mm above the PCB.
   - **Boards made from files before 2026-11-07** (the JST's two holes sit 3 mm closer to the top edge than
     on the current board): the connector's body lands on the socket of the key to its right, so it can't be
     fitted. Leave it off and
     solder the battery leads straight into its two holes (+ into the oval pad 2, − into pad 1).
5. **nice!nano:** the controller mounts on the back, components facing **away** from the PCB, on standard
   male header pins with 2.5 mm plastic spacers.
   - Fit pins **only** where the PCB has holes: 16 pins (RAW, RST, GND ×2, P0, P1, P4–P8, P14–P16, P18,
     P19). The other 8 positions sit over switch pads and are left off on purpose.
   - Trim the pins on the front to about 1.4 mm, **except** the 7 pins in the row nearer the board's left
     edge: RAW, GND, RST at the USB end, and P18, P15, P14, P16 at the far end. Those 7 come up
     *under* the two switches above the nano (2nd column, top two rows). The switch bottom sits flat on the
     PCB there. Cut them **flush** and file the solder flat (≤ ~0.2 mm), or the switches won't seat. If you
     socket the nano, the socket tails there need the same treatment.
6. **Battery:**
   - **Check polarity first.** On the JST footprint, the oval pad (pad 2) is **battery +** and the
     squarer pad (pad 1) is **battery −**. Many cheap LiPos have their plug wired the other way round.
     Measure with a multimeter before plugging in.
   - Stick the 301230 into the floor pocket with thin double-sided tape. Its lead runs from the notch at the
     pocket's end to the JST.
7. **Plate, stabilizers and switches:**
   - Clip the stabilizers into the plate. The wire bar faces the middle of the board.
   - Press the switches into the plate.
   - Lower the plate onto the PCB so the switch pins enter the sockets.
8. **Into the case:** angle the PCB in at the back first and slide it back, so the power lever slips
   through its window (it pokes about 0.5 mm out of the back) and the USB-C port slides into its window
   (it sits inside the wall, so it can't drop in from above). Then drop
   the front onto the pillars.
9. **Screws:** fit the countersunk M2 screws through the plate. Use **M2×8** at the back-left, back-right and
   centre pillars, and **M2×6** at the two front pillars. Tighten gently; they cut their own thread in the
   plastic.
10. **Keycaps.**

## 4. Firmware (ZMK)

The matrix is 4 columns × 6 rows, with diodes oriented column → row. The pin map below differs from the
original design, so the ZMK board/shield definition must match:

| Signal | nice!nano pin |
|---|---|
| Columns C1–C4 | P19, P18, P15, P14 |
| Row R1 | P16 |
| Rows R2–R6 | P4, P5, P6, P7, P8 |
| Low-battery LED (active high) | P0 (nRF P0.08) |
| Free spare | P1 |

VCC (3.3 V out) isn't connected. ZMK has no built-in low-battery LED, so blinking P0 when the battery is low
needs a small custom module. Keep it to a blink, because a steady LED drains the battery.

## Rebuilding from source

Requires ergogen v4.1.0 (`npm i -g ergogen@4.1.0`), KiCad 8 (its bundled Python provides `pcbnew`), and Java
15+ for freerouting 1.4.5.1.

1. **Generate the PCB.** Custom footprints only load when ergogen gets a *directory*. Copy `config.yaml` and
   `footprints/` into a scratch folder, then run:
   ```bash
   ergogen <scratch-folder> -o <scratch-folder>/out --clean
   ```
   This builds both boards: `not_about_money` (KS-33) and `numpad_ks33g` (KS-33G). Both come out
   unrouted. Save them as `output/pcbs/*.unrouted.kicad_pcb`, and copy `out/outlines` and `out/cases` over the
   ones in `output/`. Don't point ergogen
   at `output/` directly: `--clean` empties the whole folder, including the routed board.
2. **Route it.** Export a Specctra DSN with `pcbnew.ExportSpecctraDSN`, then route:
   ```bash
   java -jar freerouting-1.4.5.1.jar -de board.dsn -do board.ses -mp 30
   ```
   Import the result with `pcbnew.ImportSpecctraSES`. Set copper-to-edge clearance to 0.2 mm (the side
   switches sit at the board edge), then run DRC:
   ```bash
   kicad-cli pcb drc --severity-error board.kicad_pcb
   ```
3. **Gerbers:**
   ```bash
   kicad-cli pcb export gerbers --output fab/ board.kicad_pcb
   ```
   ```bash
   kicad-cli pcb export drill --output fab/ board.kicad_pcb
   ```
   Then zip the `fab/` folder.
4. **Case.** Point `BOARD` at the top of `case/build_case.py` to the board, then run it with KiCad's Python. It
   prints the stack-up, a collision report, the battery spot and the screw lengths.
   ```bash
   "C:/Program Files/KiCad/8.0/bin/python.exe" case/build_case.py
   ```
   Render the jscad files to STL with the **v1** JSCAD CLI (v2 can't run them):
   ```bash
   npm install --prefix .jscad @jscad/cli@1
   ```
   ```bash
   .jscad/node_modules/.bin/openjscad case/case_bottom.jscad -o case/case_bottom.stl
   ```
   ```bash
   .jscad/node_modules/.bin/openjscad case/case_plate.jscad -o case/case_plate.stl
   ```
5. **View it.** Serve the case folder and open `http://localhost:8765/viewer.html`:
   ```bash
   python -m http.server 8765 --directory case
   ```

`CLAUDE.md` has the full design notes: the tilt and stack-up, where each part dimension came from (datasheet
vs estimate), the stabilizer geometry, and the controller pin constraints.

## Credits and licenses

- The base design and most footprints are by [ceoloide](https://github.com/ceoloide), with contributions by
  @infused-kim and @nxtk; see `footprints/ceoloide/LICENSE`.
- Some footprints are **CC BY-NC-SA 4.0**: the nice!nano and power-switch footprints, and therefore
  `footprints/custom/mcu_nice_nano_sparse.js`, which is derived from one of them. Others are MIT. Check the
  header of each file.
- The non-commercial clause means boards built from this repo shouldn't be sold.
