# Writes PCBWay_positions.csv + PCBWay_bom.csv (PCBWay plugin format) for a board. Usage: pcbway_bom.py board out_dir
import pcbnew, sys, re, collections
b=pcbnew.LoadBoard(sys.argv[1]); O=sys.argv[2]; mm=pcbnew.ToMM
def nat(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
fps=sorted((f for f in b.GetFootprints()), key=lambda f: f.GetReference())   # plain string order, like the old file
posf=[f for f in fps if not f.IsExcludedFromPosFiles()]; fps=[f for f in fps if not f.IsExcludedFromBOM()]
mt=lambda f: 'smt' if f.GetAttributes() & pcbnew.FP_SMD else 'tht'
name=lambda f: f.GetFPID().GetLibItemName().wx_str()
with open(O+'/PCBWay_positions.csv','w',encoding='utf-8-sig',newline='') as fo:
    fo.write('pos_x,pos_y,rotation,side,designator,mpn,pack,footprint,value,mount_type\r\n')
    for f in posf:
        p=f.GetPosition()
        fo.write('%s,%s,%s,%s,%s,,,%s,%s,%s\r\n'%(round(mm(p.x),4),round(-mm(p.y),4),f.GetOrientationDegrees(),'bottom' if f.IsFlipped() else 'top',f.GetReference(),name(f),f.GetValue() if f.GetValue()!='' else '',mt(f)))
g=collections.OrderedDict()
for f in fps: g.setdefault((name(f),f.GetValue(),mt(f)),[]).append(f.GetReference())
with open(O+'/PCBWay_bom.csv','w',encoding='utf-8-sig',newline='') as fo:
    fo.write('Designator,Quantity,Value,Footprint,Package,MPN,DNP,Mount_Type\r\n')
    for (n,v,m),refs in sorted(g.items(), key=lambda kv: kv[1][0]):
        d=', '.join(refs); d='"%s"'%d if len(refs)>1 else d
        fo.write('%s,%d,%s,%s,,,,%s\r\n'%(d,len(refs),v,n,m))
