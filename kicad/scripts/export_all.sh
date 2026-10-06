#!/bin/bash
# Regenerate every fab output from kicad/numpad.kicad_pcb (run from anywhere, after the board changes):
#   kicad/fab/            gerbers + drill + map + drc-report.txt + numpad-gerbers.zip
#   kicad/numpad.kicad_pcb.zip    PCBWay package (same files/format as PCBWay's KiCad plugin)
#   kicad/gerber_render_top/bottom.png
# Both recipes were checked against the 2026-10-01 exports of the old board: identical except timestamps.
set -e
K8="C:/Program Files/KiCad/8.0/bin/kicad-cli.exe"; K10="C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"   # 10 only for IPC-D-356
PY="C:/Program Files/KiCad/8.0/bin/python.exe"
HERE=$(cd "$(dirname "$0")" && pwd); cd "$HERE/.."; B=numpad.kicad_pcb
"$K8" pcb drc --severity-error --severity-warning -o drc.rpt $B >/dev/null
# fab/
rm -f fab/numpad-* fab/drc-report.txt
"$K8" pcb export gerbers --subtract-soldermask --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" -o fab/ $B >/dev/null
"$K8" pcb export drill --generate-map --map-format gerberx2 -o fab/ $B >/dev/null
cp drc.rpt fab/drc-report.txt
(cd fab && "$PY" -c "import zipfile,os; fs=sorted(f for f in os.listdir('.') if f!='numpad-gerbers.zip'); z=zipfile.ZipFile('numpad-gerbers.zip','w',zipfile.ZIP_DEFLATED); [z.write(f) for f in fs]; z.close()")
# PCBWay package
T=$(mktemp -d); mkdir "$T/g"
"$K8" pcb export gerbers --subtract-soldermask --no-protel-ext --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts,User.Comments" -o "$T/g/" $B >/dev/null
for f in "$T"/g/*.gbr; do n=$(basename "$f"); mv "$f" "$T/${n/_Silkscreen/_SilkS}"; done; rm -rf "$T/g"   # drops the .gbrjob
"$K8" pcb export drill --format excellon --excellon-units in --excellon-zeros-format decimal --excellon-separate-th --drill-origin absolute -o "$T/" $B >/dev/null
"$K10" pcb export ipcd356 -o "$T/PCBWay_netlist.ipc" $B >/dev/null
"$PY" "$HERE/pcbway_bom.py" $B "$T"
rm -f numpad.kicad_pcb.zip; (cd "$T" && "$PY" -c "import zipfile,os,sys; z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED); [z.write(f) for f in sorted(os.listdir('.'))]; z.close()" "$HERE/../numpad.kicad_pcb.zip"); rm -rf "$T"
# renders
"$PY" "$HERE/render.py" $B gerber_render
grep "^\*\* Found" drc.rpt
