// Bottom tray for "not about money" numpad (Gateron LP hotswap build)
// Sloped shell: front ~8.5mm tall, rear ~13.5mm tall. Houses switch/socket
// protrusions, PCB (on standoffs), controller and battery.
// V1 JSCAD syntax — renders on openjscad.xyz and the legacy CLI.

function main() {
    var floorT  = 1.0;     // bottom plate thickness
    var frontH  = 8.5;     // total height at the front (-y) edge
    var rearH   = 13.5;    // total height at the rear (+y) edge
    var cx = 128.5, cy = -52.5;      // board centre (ergogen frame)
    var ow = 82.9, oh = 120.9, orr = 3.45;   // outer shell size + corner radius
    var iw = 80.5, ih = 118.5, irr = 2.25;   // inner cavity size + corner radius
    var yFront = cy - oh / 2;   // -112.95
    var yRear  = cy + oh / 2;   //    7.95

    var outer = CAG.roundedRectangle({ center: [cx, cy], radius: [ow / 2, oh / 2], roundradius: orr, resolution: 32 });
    var inner = CAG.roundedRectangle({ center: [cx, cy], radius: [iw / 2, ih / 2], roundradius: irr, resolution: 32 });

    // solid block to the rear (max) height, hollowed from the floor up
    var block  = outer.extrude({ offset: [0, 0, rearH] });
    var cavity = inner.extrude({ offset: [0, 0, rearH + 6] }).translate([0, 0, floorT]);
    var tray   = block.subtract(cavity);

    // sloped top: subtract a big box whose underside is the slope plane
    // plane passes (yFront, frontH) -> (yRear, rearH)
    var alpha = Math.atan2(rearH - frontH, yRear - yFront) * 180 / Math.PI;
    var cutter = CSG.cube({ corner1: [cx - 200, 0, 0], corner2: [cx + 200, 420, 120] })
        .rotateX(alpha)
        .translate([0, yFront, frontH]);
    tray = tray.subtract(cutter);

    // PCB standoffs with M2 clearance holes
    var posts = [[109.5, -90.5], [109.5, -33.5], [128.5, -52.5], [147.5, -90.5], [147.5, -14.5]];
    var standTop = 6.5, rPost = 3.0, rHole = 1.1;
    for (var i = 0; i < posts.length; i++) {
        var p = posts[i];
        tray = tray.union(CSG.cylinder({ start: [p[0], p[1], 0], end: [p[0], p[1], standTop], radius: rPost, resolution: 32 }));
    }
    for (var j = 0; j < posts.length; j++) {
        var q = posts[j];
        tray = tray.subtract(CSG.cylinder({ start: [q[0], q[1], -1], end: [q[0], q[1], standTop + 2], radius: rHole, resolution: 32 }));
    }
    return tray;
}
