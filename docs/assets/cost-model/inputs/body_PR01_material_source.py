"""Original body panel retention PR01. CadQuery 2.7; vehicle C, millimetres.
Rebuilds frozen R01 and applies exactly the existing R02 deck bores first.
Never writes into the frozen source or R02 directories. No supplier CAD.
M6 threads use matching nominal-diameter cylindrical surfaces, not helixes:
these are assembly equivalents, NOT clearance holes or manufacturing thread CAD.
"""
from pathlib import Path
import sys, json, math, hashlib, argparse
import cadquery as cq
P=Path(__file__).resolve().parent
BODY=P.parent
sys.path.insert(0,str(BODY))
import build_body_power as b
THREAD_NOTE=('M6x1 nominal cylindrical thread-contact equivalent, diameter 6 mm; '
 'helical flanks/runout/tolerances omitted. Manufacturing callout: tap M6x1 through; '
 'this 6 mm CAD bore is NOT a clearance hole and is NOT a tap-drill diameter. '
 'Alloy, thread stripping, fastener grade, locking, preload and corrosion unqualified.')
PARTS=[]; CHANGES=[]; JOINTS=[]; WELDS=[]; SERVICE=[]; TIE_RODS=[]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def names():return {p['name']:p for p in PARTS}
def put(n,s,mat='aluminium',group='panel_retention',note='',replace=False):
 assert s.isValid() and len(s.Solids())==1,(n,s.isValid(),len(s.Solids()))
 p={'name':n,'shape':s,'material':mat,'group':group,'note':note}
 if replace:
  i=next(i for i,q in enumerate(PARTS) if q['name']==n); old=PARTS[i]
  CHANGES.append({'action':'replace','name':n,'old_volume_mm3':old['shape'].Volume(),'new_volume_mm3':s.Volume(),'reason':note})
  PARTS[i]=p
 else:
  assert n not in names(),n
  PARTS.append(p);CHANGES.append({'action':'add','name':n,'new_volume_mm3':s.Volume(),'reason':note})
 return p

def weld(a,z,note):
 WELDS.append({'a':a,'b':z,'joint':'proposed same-alloy welded attachment','note':note,'strength_qualified':False})
def washer(x,y,z):return b.cyl(6,1.6,(x,y,z)).cut(b.cyl(3.2,2,(x,y,z-.2)))
def bolt(x,y,under,L):
 s=b.cyl(3,L,(x,y,under-L)).fuse(b.cyl(5,6,(x,y,under)))
 socket=cq.Workplane('XY').polygon(6,5/math.cos(math.pi/6)).extrude(3).translate((x,y,under+3)).val()
 return s.cut(socket)
def boss(x,y,z,t=10):return b.plate(18,18,t,z,x,y).cut(b.cyl(3,t+2,(x,y,z-1)))
def normal_y(s,sg,x,z):return s.rotate((0,0,0),(1,0,0),-90*sg).translate((x,0,z))

def baseline():
 b.PARTS.clear();b.PROXIES.clear();b.build();b.finish_seams()
 PARTS.extend(dict(p) for p in b.PARTS)
 patch=json.loads((BODY/'R02/body_attachment_patch.json').read_text())
 assert sha(BODY/'body_power_R01.step')==patch['target_sha256_before_patch']
 deck=names()['main_base_deck_3mm']
 for h in patch['holes']:
  x,y,_=[a*1000 for a in h['axis_C_m']];lo,hi=h['cut_z_mm']
  deck['shape']=deck['shape'].cut(b.cyl(h['diameter_mm']/2,hi-lo,(x,y,lo)))
 assert len(patch['holes'])==28
 deck['note']+=' Preserved R02: 28 electrical carrier deck bores, diameter 6.6 mm.'
 return {p['name']:p['shape'] for p in PARTS}

HATCHES=[('rear_controller_hatch',-1900,-1144,-450,450,337),('battery_hatch',-1125,-475,-360,360,337),('payload_tool_hatch',-456,550,-450,450,337),('front_tool_hatch',1203,1697,-513,513,297)]
def clear_existing_bosses(s):
 # Support ledges fit around separately retained tapped bosses, never occupy them.
 bb=s.BoundingBox()
 for p in PARTS:
  if '_nutplate_' not in p['name']:continue
  pb=p['shape'].BoundingBox()
  if bb.xmin<pb.xmax and pb.xmin<bb.xmax and bb.ymin<pb.ymax and pb.ymin<bb.ymax and bb.zmin<pb.zmax and pb.zmin<bb.zmax:
   s=s.cut(b.box(pb.xlen,pb.ylen,pb.zlen,((pb.xmin+pb.xmax)/2,(pb.ymin+pb.ymax)/2,(pb.zmin+pb.zmax)/2)))
 return s

def hatches():
 for n,xlo,xhi,ylo,yhi,z in HATCHES:
  cx=(xlo+xhi)/2
  pts=[(xlo+14,ylo+14),(xhi-14,ylo+14),(xlo+14,yhi-14),(xhi-14,yhi-14),(cx,ylo+14),(cx,yhi-14)]
  fixed=[n+'_weld_flange'];loose=[n+'_removable_lid',n+'_gasket']
  for i,(x,y) in enumerate(pts,1):
   bn=n+f'_M6_{i}';np=n+f'_nutplate_{i}';wn=n+f'_M6_washer_{i}'
   put(np,boss(x,y,z-10),'aluminium','hatch_retention',THREAD_NOTE+' 18x18x10 same-alloy weld-in tapped boss replaces clearance-bored steel placeholder.',True)
   put(bn,bolt(x,y,z+9.6,20),'fastener','hatch_retention','Original M6x20 ISO 4762 nominal envelope: head diameter 10, height 6, socket AF5. '+THREAD_NOTE,True)
   put(wn,washer(x,y,z+8),'fastener','hatch_retention','M6 ISO 7089 nominal washer: OD12 ID6.4 thickness1.6 mm.')
   weld(np,n+'_weld_flange','Weld boss perimeter to underside of same-alloy flange; weld sizing and distortion TBD.')
   JOINTS.append({'id':bn,'screw':bn,'holder':np,'washer':wn,'cover':n+'_removable_lid','gasket':n+'_gasket','flange':n+'_weld_flange','axis_C_mm':[x,y,z], 'direction':[0,0,1],'bolt_nominal':'ISO 4762 M6x20','length_mm':20,'underhead_mm':z+9.6,'grip_mm':9.6,'nominal_thread_engagement_mm':10,'tip_protrusion_mm':.4,'female_thread_callout':'M6x1 through 10 mm','clearance_diameter_mm':6.6,'thread_equivalent_diameter_mm':6,'washer_mm':[12,6.4,1.6],'tool':'5 mm AF hex key; axial access cylinder diameter 12 for 60 mm above head','service_axis':[0,0,1]})
   fixed.append(np);loose += [bn,wn]
  SERVICE.append({'name':n,'removable':loose,'retained_on_body':fixed,'procedure':'Remove six M6 screws and washers from above; lift lid vertically; gasket remains separable. Tapped bosses stay welded to flange. Screw/washer retention during removal is not captive.','required_tool':'5 mm AF hex key','weatherproof':False})
 # End support ledges bridge actual 1 mm partition gaps with broad plate support.
 for n,x0,x1,wall in [('rear_hatch_partition_ledge',-1163,-1143,'controller_battery_partition'),('payload_hatch_partition_ledge',-457,-437,'battery_tool_partition')]:
  put(n,clear_existing_bosses(b.plate(x1-x0,860,3,334,(x0+x1)/2,0)),note='Original 3 mm ledge abuts vertical partition and supports hatch flange underside. Same-alloy welded joint, unqualified.')
  weld(n,wall,'860 mm butt seam at partition face; qualification pending.')
  weld(n,'rear_controller_hatch_weld_flange' if n.startswith('rear') else 'payload_tool_hatch_weld_flange','Flange bears over 19 mm ledge; same-alloy weld/fit detail.')
 # Front hatch originally met side-wall top only at an edge. Real under-flange ledges.
 for sign,label in [(1,'left'),(-1,'right')]:
  n='front_hatch_'+label+'_support_ledge';put(n,clear_existing_bosses(b.plate(494,20,3,294,1450,sign*503)),note='20x3 mm continuous ledge welded to front tool side; supports existing flange.')
  weld(n,'front_tool_'+label+'_side','494 mm edge seam to side wall.');weld(n,'front_tool_hatch_weld_flange','20 mm bearing band under flange.')
 for n,xa,xb in [('front_hatch_rear_support_ledge',1203,1223),('front_hatch_nose_support_ledge',1677,1703)]:
  s=b.plate(xb-xa,986,3,294,(xa+xb)/2)
  s=clear_existing_bosses(s.cut(names()['front_sloped_service_nose']['shape']))
  put(n,s,note='Original under-flange support cross strip; nose end fitted by subtracting actual sloped nose, no positive-volume clash.')
  weld(n,'front_tool_hatch_weld_flange','Broad flange bearing contact.')
  weld(n,'front_tool_rear_wall' if 'rear' in n else 'front_sloped_service_nose','Rear butt seam / fitted nose seam, unqualified.')

def side_covers():
 for sg,label in [(1,'left'),(-1,'right')]:
  for j,(xc,ll) in enumerate([(-800,480),(390,250)],1):
   cover=f'{label}_side_service_cover_{j}';fixed=[];loose=[cover]
   pts=[(xc+dx,184+dz) for dx in [-(ll/2-18),(ll/2-18)] for dz in [-20,20]]
   for k,(x,z) in enumerate(pts,1):
    clip=f'{label}_service_nutclip_{j}_{k}';np=clip+'_tapped_boss';bn=clip+'_M6x20';wn=clip+'_washer'
    s=b.box(40,3,40,(x,sg*511.5,z));s=b.holes(s,[(x,z)],3.3,axis='Y',start=-600,length=1200)
    put(clip,s,'aluminium','side_cover_retention','Original 40x40x3 same-alloy backing clip; actual Ø6.6 clearance bore, supported beyond cutout edges. Replaces unweldable steel-to-aluminium placeholder.',True)
    put(np,normal_y(boss(0,0,497,13),sg,x,z),'aluminium','side_cover_retention',THREAD_NOTE+' Original 18x18x13 tapped backing block, welded to clip inner face.')
    put(bn,normal_y(bolt(0,0,517.6,20),sg,x,z),'fastener','side_cover_retention','ISO 4762 nominal M6x20 screw installed from outside. '+THREAD_NOTE)
    put(wn,normal_y(washer(0,0,516),sg,x,z),'fastener','side_cover_retention','ISO 7089 nominal M6 washer OD12 ID6.4 t1.6.')
    weld(clip,'main_'+label+'_side_3mm','Clip overlaps cutout at end and top/bottom; same-alloy weld outside removable cover footprint.')
    weld(np,clip,'Same-alloy boss perimeter welded to backing clip.')
    JOINTS.append({'id':bn,'screw':bn,'holder':np,'washer':wn,'cover':cover,'flange':clip,'axis_C_mm':[x,sg*513,z],'direction':[0,sg,0],'bolt_nominal':'ISO 4762 M6x20','length_mm':20,'underhead_mm':517.6,'grip_mm':7.6,'nominal_thread_engagement_mm':12.4,'tip_recess_mm':.6,'female_thread_callout':'M6x1 through 13 mm','clearance_diameter_mm':6.6,'thread_equivalent_diameter_mm':6,'washer_mm':[12,6.4,1.6],'tool':'5 mm AF hex key; axial access cylinder diameter12 for60 mm outward','service_axis':[0,sg,0]})
    fixed += [clip,np];loose += [bn,wn]
   SERVICE.append({'name':cover,'removable':loose,'retained_on_body':fixed,'procedure':'Remove four M6 screws and washers from outside, translate panel outward 20 mm, then lift. Clips and tapped blocks remain welded to side wall.','required_tool':'5 mm AF hex key','weatherproof':False})

def supports():
 # Actual old body#37/38/40/41/43/44/46/47. Four mm pad thickness had
 # erroneously been copied into stop-plate elevation, leaving all stops floating.
 for i,(x,y) in enumerate([(x,y) for x in (-950,-650) for y in (-110,110)],1):
  for sg in (-1,1):
   n=f'battery_{i}_stop_{sg}';put(n,b.box(260,3,32,(x,y+sg*104,-61)),'restraint','battery_support','Bottom extended from Z-73 to Z-77 to bear on well floor; 4 mm gap removed. Original 260x3x32 stop, same-alloy welded to well floor. Load qualification pending.',True)
   weld(n,'battery_well_floor_3mm','260 mm continuous bottom edge; proposed fillet weld both accessible sides, sizing TBD.')
 # Shelf-and-gusset supports attach each floating duct to named partitions.
 specs=[(1,-1863,-1173,-1897,-1143,'rear_bulkhead_3mm','controller_battery_partition'),(2,-1125,-475,-1140,-460,'controller_battery_partition','battery_tool_partition'),(3,-440,520,-457,547,'battery_tool_partition','arm_facing_bulkhead_3mm')]
 for i,x0,x1,wa,wb,an,bn in specs:
  for label,wall,tip,host in [('rear',wa,x0+25,an),('front',wb,x1-25,bn)]:
   xa,xb=sorted([wall,tip]);s=b.plate(xb-xa,70,3,227,(xa+xb)/2,435)
   for y in (411.5,461.5):
    # Real plate triangular gussets, integrated to the shelf. 3 mm extrusion.
    g=cq.Workplane('XZ').polyline([(wall,203),(wall,227),(tip,227)]).close().extrude(3).translate((0,y,0)).val();s=s.fuse(g)
   n=f'cable_duct_{i}_{label}_welded_support';put(n,s,note='Original 3 mm shelf with two 24 mm-deep triangular gussets; 25 mm bearing overlap under duct floor, broad end seam to named partition. Weld strength and duct span deflection unqualified.')
   weld(n,host,'70 mm shelf end seam plus two 24 mm gusset roots to partition.')
   weld(n,f'cable_duct_floor_{i}','25x70 mm bearing overlap, duct welded at support edges.')
  for y in (400,470):weld(f'cable_duct_floor_{i}',f'cable_duct_side_{i}_{y}','Existing floor/side edge connection to become same-alloy welded duct.')



def battery_tie_rods():
 # Connection-completeness correction only. The existing 12 mm gap between
 # crossbar and battery envelope remains an explicit, unresolved restraint gate.
 for i,x in enumerate((-950,-650),1):
  for y in (-235,235):
   stem=f'battery_retention_stud_{i}_{y}'
   put(stem,b.cyl(4,325,(x,y,-93)),'fastener','battery_support','Original cut-to-length M8x1.25 threaded-rod nominal cylinder, 325 mm long Z-93..232. No helix/grade/preload/terminal insulation qualification.',True)
   row={'id':stem,'rod':stem,'axis_C_mm':[x,y,0],'length_mm':325,'pitch_mm':1.25,'nominal_diameter_mm':8,'nut_engagement_mm':6.5,'end_protrusion_mm':4.9,'crossbar':f'battery_retention_crossbar_{i}','floor':'battery_well_floor_3mm','battery_envelope_to_crossbar_gap_mm':12,'battery_restraint_qualified':False,'ends':[]}
   for tag,nz,wz,host in [('bottom',-88.1,-81.6,'battery_well_floor_3mm'),('top',220.6,219,f'battery_retention_crossbar_{i}')]:
    nn=f'battery_retention_nut_{i}_{y}_{tag}';wn=f'battery_retention_washer_{i}_{y}_{tag}'
    nut=cq.Workplane('XY').polygon(6,13/math.cos(math.pi/6)).circle(4).extrude(6.5).translate((x,y,nz)).val()
    put(nn,nut,'fastener','battery_support','ISO 4032 nominal M8 nut AF13 height6.5; matching diameter8 cylindrical nominal thread interface, coarse pitch1.25 metadata. No helix or finished-thread tolerance claim.',True)
    ws=b.cyl(8,1.6,(x,y,wz)).cut(b.cyl(4.2,2,(x,y,wz-.2)))
    put(wn,ws,'fastener','battery_support','ISO 7089 M8 nominal washer OD16 ID8.4 thickness1.6. Bears against actual well-floor underside or crossbar top; no local panel strength claim.')
    row['ends'].append({'name':tag,'nut':nn,'washer':wn,'bearing_part':host,'nut_z_mm':[nz,nz+6.5],'washer_z_mm':[wz,wz+1.6]})
   TIE_RODS.append(row)


def build():
 PARTS.clear();CHANGES.clear();JOINTS.clear();WELDS.clear();SERVICE.clear();TIE_RODS.clear()
 original=baseline();print('Base R02 rebuilt',flush=True);hatches();print('Hatches rebuilt',flush=True);side_covers();supports();battery_tie_rods();print('All retention parts built',len(PARTS),flush=True)
 return original

def export(out):
 out.mkdir(parents=True,exist_ok=True)
 ass=cq.Assembly(name='body_panel_retention_PR01')
 for p in PARTS:ass.add(p['shape'],name=p['name'],color=cq.Color(*b.MATS[p['material']]['color']))
 ass.export(str(out/'body_power_panel_retained_PR01.step'))
 b.export_glb(PARTS,out/'body_power_panel_retained_PR01.glb')
 changed=[p for p in PARTS if p['name'] in {c['name'] for c in CHANGES}]
 ass=cq.Assembly(name='body_retention_delta_PR01')
 for p in changed:ass.add(p['shape'],name=p['name'],color=cq.Color(*b.MATS[p['material']]['color']))
 ass.export(str(out/'body_retention_delta_PR01.step'));b.export_glb(changed,out/'body_retention_delta_PR01.glb')
 nonrear=[p for p in changed if not (p['name'].startswith('rear_controller_hatch') or p['name']=='rear_hatch_partition_ledge')]
 ass=cq.Assembly(name='body_retention_delta_nonrear_PR01')
 for p in nonrear:ass.add(p['shape'],name=p['name'],color=cq.Color(*b.MATS[p['material']]['color']))
 ass.export(str(out/'body_retention_delta_nonrear_PR01.step'));b.export_glb(nonrear,out/'body_retention_delta_nonrear_PR01.glb')
 manifest={'revision':'PR01','units':'STEP mm; GLB metres Z-up','integration_rule':'Either replace entire body R02 with body_power_panel_retained_PR01 OR replace listed existing named parts and add new parts. Never layer replacement parts over originals. Full-body output includes every original body part and all 28 R02 bores. Other body patches must compose by name.','base_generator_sha256':sha(BODY/'build_body_power.py'),'baseline_R01_step_sha256':sha(BODY/'body_power_R01.step'),'R02_step_sha256':sha(BODY/'R02/body_power_R02.step'),'R02_deck_holes_preserved':28,'generator_sha256':sha(__file__),'unfrozen_rear_service_enclosure_group':{'status':'Optional; electrical raised-module redesign pending. Do not stack old hatch underneath an inaccessible new enclosure.','body_names_to_remove_if_replaced':[p['name'] for p in PARTS if p['name'].startswith('rear_controller_hatch') or p['name']=='rear_hatch_partition_ledge'],'delta_changes_to_exclude':[c['name'] for c in CHANGES if c['name'].startswith('rear_controller_hatch') or c['name']=='rear_hatch_partition_ledge']},'changes':CHANGES,'retained_service_groups':SERVICE,'joints':JOINTS,'battery_tie_rods':TIE_RODS,'welded_connections':WELDS,'thread_representation':THREAD_NOTE,'qualification':'Development geometry only. No structural, fatigue, ingress, tolerance, weld, corrosion, torque or operational qualification.','outputs':{n:sha(out/n) for n in ['body_power_panel_retained_PR01.step','body_power_panel_retained_PR01.glb','body_retention_delta_PR01.step','body_retention_delta_PR01.glb','body_retention_delta_nonrear_PR01.step','body_retention_delta_nonrear_PR01.glb']}}
 (out/'replacement_addition_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'parts':len(PARTS),'changes':len(CHANGES),'retained_M6_joints':len(JOINTS),'service_groups':len(SERVICE),'outputs':manifest['outputs']}),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P);args=ap.parse_args()
 build();export(args.out)
