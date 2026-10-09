"""Original lightweight R07 candidate. Preserves R06. Not strength/fabrication approved.
Rails200x100x6; arm-supportcrosses200x100x6 at730/1070; othercrosses100x60x5.
Chosen engineering assumptions must be checked under dual-arm loads/fatigue/torsion.
"""
from generate_cad import *
def build():
 parts=[];env=[]
 for side,y in [('left',460),('right',-460)]:
  s,e=rhs('X',4000,100,200,6,(0,y,0),ro=12);parts.append(('main_rail_'+side,s));env.append(e)
 xs=[-1950,-1200,-400,730,1070,1300,1650,1950]
 for i,x in enumerate(xs):
  if i in [3,4]:s,_=rhs('Y',860,100,200,6,(x,0,0),ro=12)
  else:s,_=rhs('Y',860,60,100,5,(x,0,50),ro=10)
  for e in env:s=s.cut(e)
  parts.append((f'crossmember_{i+1:02d}',s))
 holes=[]
 for side,y in [('left',300),('right',-300)]:
  s=box(400,400,30,(900,y,115))
  for a in range(0,360,60):
   xh=900+105*math.cos(math.radians(a));yh=y+105*math.sin(math.radians(a))
   s=s.cut(cq.Workplane('XY').center(xh,yh).circle(4.25).extrude(32).translate((0,0,99)))
   holes.append([xh,yh])
  parts.append(('arm_deck_'+side,s.val()))
 for j,x in enumerate([-1200,-400,1650]):
  for side,sign in [('left',1),('right',-1)]:
   s=cq.Workplane('YZ').polyline([(sign*410,10),(sign*310,10),(sign*410,90)]).close().extrude(8).translate((x+30,0,0)).val()
   parts.append((f'gusset_{j+1}_{side}',s))
 r=export(parts,'frame_R07')
 assert r['solid_count']==18 and np.allclose(r['bbox_m'],[4,1.02,.23],atol=1e-8)
 access=[]
 for x,y in holes:
  tool=cq.Workplane('XY').center(x,y).circle(7.5).extrude(220).translate((0,0,-120)).val()
  for name,s in parts:
   if not name.startswith('arm_deck'):
    ba,bb=exact_bounds(tool),exact_bounds(s)
    if any(ba[k+3]<bb[k]-1e-5 or bb[k+3]<ba[k]-1e-5 for k in range(3)):continue
    v=tool.intersect(s).Volume()
    if v>1e-4:access.append({'hole':[x,y],'part':name,'intersection_mm3':v})
 assert not access
 reached={parts[0][0]}
 while True:
  nxt=reached|{b for a,b,d in r['zero_gap_contacts'] if a in reached}|{a for a,b,d in r['zero_gap_contacts'] if b in reached}
  if nxt==reached:break
  reached=nxt
 assert len(reached)==18
 r.update(pilot_holes={'count':12,'diameter_mm':8.5,'PCD_mm':210,'phase_deg':0,'entry_centers_mm':[[x,y,130]for x,y in holes]},machining_access_test={'cylinder_diameter_mm':15,'Z_span_mm':[-120,100],'obstructions':access,'scope':'belowdeck drill/taprunout envelope, excludesdeck itself; not actual machine/tool geometry'},contact_graph_connected=True,changes_from_R06=['200x100x6 mainrails, R12/R6 assumedstockradii','arm-supportcrosses200x100x6 centers730/1070 clearpilotrunout','6secondarycrosses100x60x5 topZ100','gussets recoped to newsecondarycrosswidth'],structural_status='UNQUALIFIED candidate; no strength, torsion, fatigue, welding or arm-reaction release')
 (P/'frame_R07_verification.json').write_text(json.dumps(r,indent=2))
 with(P/'frame_R07_cutlist.csv').open('w')as f:
  w=csv.writer(f);w.writerow(['part','qty','stock','blank_length_mm','notes']);w.writerow(['mainrails',2,'RHS200x100x6 R12/R6',4000,'supplierradii/grade TBD']);w.writerow(['armcrosses',2,'RHS200x100x6 R12/R6',860,'centers730/1070;cope to mainrail']);w.writerow(['secondarycrosses',6,'RHS100x60x5 R10/R5',860,'topZ100;cope to mainrail']);w.writerow(['decks',2,'plate400x400x30',400,'same12pilots0degphase']);w.writerow(['gussets',6,'triangularplate100x80x8',100,'weldedgeprep TBD'])
 print('R07 COMPLETE',json.dumps(r['assembly_properties']),flush=True)
if __name__=='__main__':build()
