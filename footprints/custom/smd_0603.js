// Two-pad 0603 (1608 metric) SMD part with hand-solder pads: an LED or a resistor.
//
// Params:
//    designator: default is 'LED'
//    side: F or B, the copper side the part sits on
//    polarized: default true; adds a cathode bar on the silkscreen next to the `to` pad
//    from: net on pad 1 (LED anode)
//    to: net on pad 2 (LED cathode)
//
// Pads follow KiCad's R_0603_1608Metric_Pad1.05x0.95_HandSolder. On side B the pads are
// mirrored so the part reads the same from the back.

module.exports = {
  params: {
    designator: 'LED',
    side: 'F',
    polarized: true,
    from: { type: 'net', value: undefined },
    to: { type: 'net', value: undefined }
  },
  body: p => {
    const s = p.side
    const m = s == 'B' ? -1 : 1   // mirror x on the back
    const ax = -0.875 * m, kx = 0.875 * m
    const silk = (x0, y0, x1, y1) =>
      `(fp_line (start ${x0} ${y0}) (end ${x1} ${y1}) (layer "${s}.SilkS") (stroke (width 0.12) (type solid)))`
    const fab = (x0, y0, x1, y1) =>
      `(fp_line (start ${x0} ${y0}) (end ${x1} ${y1}) (layer "${s}.Fab") (stroke (width 0.1) (type solid)))`
    const bar = p.polarized ? silk(1.65 * m, -0.7, 1.65 * m, 0.7) : ''
    return `
    (footprint "custom:smd_0603"
        (layer "${s}.Cu")
        ${p.at}
        (property "Reference" "${p.ref}"
            (at 0 -1.5 ${p.r})
            (layer "${s}.SilkS")
            ${p.ref_hide}
            (effects (font (size 0.8 0.8) (thickness 0.12)) ${s == 'B' ? '(justify mirror)' : ''})
        )
        (attr smd)
        ${silk(-0.25, -0.7, 0.25, -0.7)}
        ${silk(-0.25, 0.7, 0.25, 0.7)}
        ${bar}
        ${fab(-0.8, -0.4, 0.8, -0.4)}
        ${fab(0.8, -0.4, 0.8, 0.4)}
        ${fab(0.8, 0.4, -0.8, 0.4)}
        ${fab(-0.8, 0.4, -0.8, -0.4)}
        (fp_rect (start -1.65 -0.73) (end 1.65 0.73) (layer "${s}.CrtYd") (stroke (width 0.05) (type solid)) (fill none))
        (pad "1" smd roundrect (at ${ax} 0 ${p.r}) (size 1.05 0.95) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.25) ${p.from.str})
        (pad "2" smd roundrect (at ${kx} 0 ${p.r}) (size 1.05 0.95) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.25) ${p.to.str})
    )
    `
  }
}
