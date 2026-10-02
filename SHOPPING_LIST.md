# Shopping list

Everything needed to build one numpad: 21 keys, wireless, Gateron low-profile hotswap.
Quantities are per keyboard. Buy a few spares of the small parts.

## Electronics

| Qty | Part | Exact part / spec | Notes |
|---|---|---|---|
| 1 | PCB | 2-layer, 1.6 mm FR-4, from `kicad/fab/numpad-gerbers.zip` | Any fab (JLCPCB, PCBWay, …). The 3 stabilizer cutouts are in the board outline, so no extra milling is needed. |
| 1 | Controller | **nice!nano v2** | Wireless nRF52840 (ZMK). |
| 16 | Header pins | 2.54 mm single-row male headers with standard **2.5 mm** plastic | Only 16 of the 24 positions are used (see the README). Buy a 1×40 strip. |
| 21 | Hotswap sockets | **Gateron Low Profile Hot-swap 2.0, KS-2P02B01-02** | Must be the **low-profile** version (-02). The regular -01 socket doesn't fit. Sold in packs of 70/110. |
| 21 | Diodes | 1N4148W, **SOD-123** | |
| 1 | Reset button | **Panasonic EVQ-PUA02K** (or EVQ-PUC02K / EVQ-PUL02K) | Side-push SMD, 4.7 × 3.5 mm. PUA02K is the easy-to-find one; it has no locating pegs, so the two small holes stay empty. Not EVQ-PUD02K (3.2 mm deep). |
| 1 | Power switch | **MSK-12C02-style side slide switch, H = 2.5 mm** (7-pin SMD, 6.65 × 2.7 × 1.4 body, 1.5 mm pin pitch) | Must be the **2.5 mm lever** version, so it sticks ~0.5 mm out of the case. The 1.5/2.0 versions (and the Alps SSSS811101) fit the pads but end inside the wall. |
| 1 | Battery connector | **JST PH S2B-PH-K-S** | 2-pin, 2.0 mm, side entry, through-hole. |
| 1 | Low-battery LED | **Lite-On LTST-C191KRKT** (0603, red, 0.55 mm tall) | Any 0603 LED up to ~1.4 mm tall fits. |
| 1 | LED resistor | 1 kΩ, 0603 | |
| 1 | Battery | **301230 LiPo**, 3.7 V, ~110 mAh, 3 × 12 × 30 mm, with protection circuit and a **JST PH 2.0** plug | The case has a pocket sized for this cell. **Check the plug polarity** before connecting it (see the README). |

## Switches and keycaps

| Qty | Part | Exact part / spec | Notes |
|---|---|---|---|
| 21 | Switches | **Gateron KS-33 Low Profile 2.0** (e.g. Brown, KS-33E10B055NN-Y24) | Any KS-33 variant. Sold in packs of 35/70/110. |
| 3 | Stabilizers | **Gateron Low Profile Plate-Mounted Stabilizer 2U, KS-57B210T** | For the "0", "+" and "Enter" keys. |
| 18 | Keycaps, 1u | Low-profile keycaps for Gateron LP / KS-33 switches, **18 mm** | Standard-height MX keycaps are too tall for this build. |
| 1 | Keycap, 2u horizontal | Same profile, 2u wide (37 × 18 mm) | "0" key. |
| 2 | Keycaps, 2u vertical | Same profile, 2u tall (18 × 37 mm) | "+" and "Enter". |

## Case and hardware

| Qty | Part | Exact part / spec | Notes |
|---|---|---|---|
| 1 | Case bottom (3D print) | `case/case_bottom.stl` | PLA or PETG, 0.2 mm layers, no supports needed. |
| 1 | Switch plate (3D print) | `case/case_plate.stl` | Print it **upside down** (top face on the bed), because the rim and spacer posts are on its underside. |
| 3 | Screws | **M2 × 8 countersunk** (DIN 965 / ISO 7046), self-tapping or thread-forming for plastic | For the pillars at the back-left, back-right and centre. |
| 2 | Screws | **M2 × 6 countersunk**, same type | For the two front pillars, which are shorter. |
| 1 | Double-sided tape | Thin foam or VHB strip, ~10 × 25 mm | Holds the battery in its pocket. |
| 4 | Rubber feet (optional) | Small adhesive bumpers, ≤ 8 mm | |

## Tools

- Soldering iron with a fine tip, solder, flux.
- Flush cutters, for trimming the header pins and the JST pins.
- Rotary tool or a fine file, to shorten one solder tab on 3 of the hotswap sockets (see the README).
- Tweezers, a multimeter, and a USB-C cable for flashing.
- 3D printer, or a printing service.
