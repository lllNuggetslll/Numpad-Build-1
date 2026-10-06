# Flat 4-colour renders like the originals (copper, silk, mask openings, outline). usage: render.py board.kicad_pcb out_prefix -> out_prefix_top.png / _bottom.png (20 px/mm, 3 px margin; both seen from the top)
import pcbnew, sys
from PIL import Image, ImageDraw, ImageChops
b = pcbnew.LoadBoard(sys.argv[1]); PX = 20.0; M = 3
_o = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(_o); bb = _o.BBox()
x0, y0 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
W = int(round(pcbnew.ToMM(bb.GetWidth()) * PX)) + 2 * M; H = int(round(pcbnew.ToMM(bb.GetHeight()) * PX)) + 2 * M
def layer_mask(layer, mirror):
    ps = pcbnew.SHAPE_POLY_SET(); b.ConvertBrdLayerToPolygonalContours(layer, ps)
    im = Image.new('1', (W, H), 0); d = ImageDraw.Draw(im)
    def pts(chain):
        out = []
        for i in range(chain.PointCount()):
            p = chain.CPoint(i); x = (pcbnew.ToMM(p.x) - x0) * PX + M; y = (pcbnew.ToMM(p.y) - y0) * PX + M
            out.append(((W - 1 - x) if mirror else x, y))
        return out
    for i in range(ps.OutlineCount()):
        d.polygon(pts(ps.Outline(i)), fill=1)
        for h in range(ps.HoleCount(i)): d.polygon(pts(ps.Hole(i, h)), fill=0)
    return im
def render(cu, mask, silk, mirror, fn):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    # copper, then silkscreen, then mask openings (pads/holes) on top, then the outline
    for layer, col in ((cu, (40, 143, 40)), (silk, (255, 255, 255)), (mask, (153, 153, 153)), (pcbnew.Edge_Cuts, (255, 255, 255))):
        img.paste(Image.new('RGB', (W, H), col), (0, 0), layer_mask(layer, mirror))
    img.save(fn)
render(pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_SilkS, False, sys.argv[2] + '_top.png')
render(pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_SilkS, False, sys.argv[2] + '_bottom.png')
