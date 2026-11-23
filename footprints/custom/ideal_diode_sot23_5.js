// LTC4411 ideal diode (Analog Devices, SOT-23-5 / ThinSOT), for charging the battery while the power
// switch is off. Pins: 1 IN (anode), 2 GND, 3 CTL (active-high shutdown, tied to GND here = always on),
// 4 STAT (open drain, unused), 5 OUT (cathode). Needs a 1 uF ceramic on OUT (separate footprint).
//
// Params:
//    designator: default 'IC'
//    side: F or B
//    IN, OUT, GND: nets. CTL (pin 3) is put on GND as well.
//    STAT (pin 4) is left unconnected.
//
// Pads follow KiCad's Package_TO_SOT_SMD:SOT-23-5. On side B they are mirrored in x so the part reads
// the same from the back (pin 1 top right when seen from the back).

module.exports = {
  params: {
    designator: 'IC',  // not 'U': ergogen evaluates that as its unit variable u (19.05)
    side: 'B',
    IN: { type: 'net', value: undefined },
    OUT: { type: 'net', value: undefined },
    GND: { type: 'net', value: 'GND' },
  },
  body: p => {
    const s = p.side
    const m = s == 'B' ? -1 : 1
    const L = -1.1375 * m, R = 1.1375 * m
    const silk = (x0, y0, x1, y1) =>
      `(fp_line (start ${x0} ${y0}) (end ${x1} ${y1}) (layer "${s}.SilkS") (stroke (width 0.12) (type solid)))`
    const fab = (x0, y0, x1, y1) =>
      `(fp_line (start ${x0} ${y0}) (end ${x1} ${y1}) (layer "${s}.Fab") (stroke (width 0.1) (type solid)))`
    const pad = (n, x, y, net) =>
      `(pad "${n}" smd roundrect (at ${x} ${y} ${p.r}) (size 1.325 0.6) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.25) ${net})`
    return `
    (footprint "custom:ideal_diode_sot23_5"
        (layer "${s}.Cu")
        ${p.at}
        (property "Reference" "${p.ref}"
            (at 0 -2.4 ${p.r})
            (layer "${s}.SilkS")
            ${p.ref_hide}
            (effects (font (size 0.8 0.8) (thickness 0.12)) ${s == 'B' ? '(justify mirror)' : ''})
        )
        (property "Value" "LTC4411" (at 0 2.4 ${p.r}) (layer "${s}.Fab") (effects (font (size 0.8 0.8) (thickness 0.12)) ${s == 'B' ? '(justify mirror)' : ''}))
        (attr smd)
        ${silk(0.8 * m, -1.56, -0.8 * m, -1.56)}
        ${silk(-0.8 * m, 1.56, 0.8 * m, 1.56)}
        ${silk(-1.85 * m, -1.45, -1.85 * m, -1.25)}
        ${fab(-0.4 * m, -1.45, 0.8 * m, -1.45)}
        ${fab(0.8 * m, -1.45, 0.8 * m, 1.45)}
        ${fab(0.8 * m, 1.45, -0.8 * m, 1.45)}
        ${fab(-0.8 * m, 1.45, -0.8 * m, -1.05)}
        ${fab(-0.8 * m, -1.05, -0.4 * m, -1.45)}
        (fp_rect (start -2.05 -1.7) (end 2.05 1.7) (layer "${s}.CrtYd") (stroke (width 0.05) (type solid)) (fill none))
        ${pad(1, L, -0.95, p.IN.str)}
        ${pad(2, L, 0, p.GND.str)}
        ${pad(3, L, 0.95, p.GND.str)}
        ${pad(4, R, 0.95, '')}
        ${pad(5, R, -0.95, p.OUT.str)}
    )
    `
  }
}
