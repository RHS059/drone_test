"""Original, parametric body integration R01. Native CAD mm, X forward/Y left/Z up.
This is engineered manufacturing-development geometry, NOT a qualified rover design.
Supplier dimensional reservations are exported separately from original component CAD.
No supplier CAD geometry is copied. See README.md and SOURCES.json.
"""
from pathlib import Path
import cadquery as cq, numpy as np
import json, math, struct, csv, hashlib
P=Path(__file__).resolve().parent
REFERENCE_FRAME=P/'reference_frame_R06.step'
PARTS=[]; PROXIES=[]
MATS={
 'aluminium':{'density':2700,'color':[.57,.54,.46,1],'assumption':'5083-like aluminium density; alloy/temper and weld procedure not qualified'},
 'lid':{'density':2700,'color':[.66,.62,.53,1],'assumption':'5083-like aluminium density; alloy/temper TBD'},
 'steel':{'density':7850,'color':[.21,.25,.28,1],'assumption':'generic carbon steel density; grade not specified'},
 'fastener':{'density':7850,'color':[.66,.69,.70,1],'assumption':'simplified unthreaded steel fastener, strength class TBD'},
 'gasket':{'density':1200,'color':[.055,.064,.07,1],'assumption':'EPDM-like nominal density, material and compression qualification pending'},
 'restraint':{'density':2700,'color':[.76,.43,.10,1],'assumption':'aluminium, unqualified strength'},
 'proxy':{'density':0,'color':[.89,.45,.10,.45],'assumption':'nonphysical dimensional envelope, not supplier CAD'}
}
def box(l,w,h,c):return cq.Workplane('XY').box(l,w,h).translate(c).val()
def plate(l,w,t,z,cx=0,cy=0):return box(l,w,t,(cx,cy,z+t/2))
def cyl(r,h,c,axis='Z'):
 wp=cq.Workplane({'Z':'XY','X':'YZ','Y':'XZ'}[axis]).circle(r).extrude(h)
 # XZ extrudes -Y by CadQuery's plane convention.
 if axis=='Y':wp=wp.translate((0,h,0))
 return wp.translate(c).val()
def add(n,s,mat='aluminium',group='body',note=''):
 assert s.isValid(),n
 PARTS.append({'name':n,'shape':s,'material':mat,'group':group,'note':note})
 return s
def holes(s,pts,r,axis='Z',start=-200,length=800):
 for a,b in pts:
  c=(a,b,start) if axis=='Z' else (start,a,b) if axis=='X' else (a,start,b)
  s=s.cut(cyl(r,length,c,axis))
 return s
def ring_rect(l,w,band,t,z,cx=0,cy=0):return plate(l,w,t,z,cx,cy).cut(plate(l-2*band,w-2*band,t+2,z-1,cx,cy))
def screw(n,x,y,z,shaft_len=15,r=3,head_r=5,head_h=4,group='fasteners'):
 # Smooth shank and socket head are deliberate simplified fastener geometry, not vendor CAD.
 s=cyl(r,shaft_len,(x,y,z-shaft_len)).fuse(cyl(head_r,head_h,(x,y,z)))
 socket=cq.Workplane('XY').polygon(6,head_r*.95).extrude(2).translate((x,y,z+head_h-2)).val()
 add(n,s.cut(socket),'fastener',group,'Nominal M6-style envelope, no thread model or strength rating.')
def hatch(n,xlo,xhi,ylo,yhi,z=337,group='hatches'):
 l=xhi-xlo;w=yhi-ylo;cx=(xlo+xhi)/2;cy=(ylo+yhi)/2
 pts=[(xlo+14,ylo+14),(xhi-14,ylo+14),(xlo+14,yhi-14),(xhi-14,yhi-14),
      (cx,ylo+14),(cx,yhi-14)]
 rim=holes(ring_rect(l,w,20,3,z,cx,cy),pts,3.3)
 gasket=holes(ring_rect(l-2,w-2,16,2,z+3,cx,cy),pts,3.3)
 lid=holes(plate(l-2,w-2,3,z+5,cx,cy),pts,3.3)
 # Two recessed finger pull slots: actual holes, not fake handles.
 for hx in [cx-l*.25,cx+l*.25]:
  slot=cq.Workplane('XY').center(hx,cy).slot2D(80,18,0).extrude(5).translate((0,0,z+4)).val();lid=lid.cut(slot)
 add(n+'_weld_flange',rim,'aluminium',group)
 add(n+'_gasket',gasket,'gasket',group,'Concept gasket with 2 mm nominal uncompressed thickness; finger holes mean lid is not weather sealed.')
 add(n+'_removable_lid',lid,'lid',group,'3 mm laser-cut lid. Finger slots require sealed insert handles before weatherproofing.')
 for i,(x,y) in enumerate(pts):screw(n+f'_M6_{i+1}',x,y,z+8,shaft_len=11,group=group)
 # Backing nut strips are separate with clearance bores. Inserts/threads not modeled.
 for i,(x,y) in enumerate(pts):
  s=plate(18,18,4,z-4,x,y).cut(cyl(3.3,6,(x,y,z-5)))
  add(n+f'_nutplate_{i+1}',s,'steel',group,'M6 rivet-nut or weld-nut finishing operation not yet selected; clearance hole modeled.')
 return (l,w)
def panel_vents(s,xcenter,zcenter,y,rows=5,cols=7,pitchx=24,pitchz=18):
 for i in range(cols):
  for j in range(rows):
   x=xcenter+(i-(cols-1)/2)*pitchx;z=zcenter+(j-(rows-1)/2)*pitchz
   s=s.cut(box(16,12,6,(x,y,z)))
 return s

def build():
 # Main enclosure base contacts the existing rails and crossmembers at Z=100.
 base=plate(2450,1026,3,100,-675)
 base=base.cut(plate(650,720,6,99,-800))
 for xc in (-1350,0):
  for sy in (-460,460):base=base.cut(box(410,144,10,(xc,sy,102)))
 # Slots accept proposed rail clamps, no holes silently added to inherited frame.
 clamp_pts=[(x,y) for x in (-1050,-550) for y in (-390,390)]
 base=holes(base,clamp_pts,5.4)
 add('main_base_deck_3mm',base,'aluminium','main_body','2.45 m laser-cut base; recessed battery-well opening; sits on frame Z=100.')
 # Full side sheets, controller-bay vents and service access holes.
 for sign,label in [(1,'left'),(-1,'right')]:
  y=sign*514.5
  s=box(2450,3,117,(-675,y,161.5)) # Z103..220, Y513..516
  s=panel_vents(s,-1525,182,y,rows=3)
  for xc in (-1050,-550):s=s.cut(box(84,12,9,(xc,y,106.5)))
  for xc in (-1350,0):
   s=s.cut(box(410,14,32,(xc,y,116)))
   s=s.cut(box(160,32,110,(xc,y,160)))
  # Side access door cutout for terminal-service bay and forward tool compartment.
  for xc,ll in [(-800,480),(390,250)]:s=s.cut(box(ll,10,66,(xc,y,184)))
  add('main_'+label+'_side_3mm',s,'aluminium','main_body')
  # Removable side service covers with 2 mm gaps, actual fastener holes along normal Y.
  for j,(xc,ll) in enumerate([(-800,480),(390,250)]):
   cover=box(ll-4,3,62,(xc,sign*514.5,184))
   pts=[(xc+dx,184+dz) for dx in [-(ll/2-18),(ll/2-18)] for dz in [-20,20]]
   cover=holes(cover,pts,3.3,axis='Y',start=-600,length=1200)
   # A horizontal finger recess through each plate (must seal for environmental qualification).
   cover=cover.cut(box(76,10,12,(xc,sign*514.5,190)))
   add(f'{label}_side_service_cover_{j+1}',cover,'lid','side_service','62 mm-high removable access panel. Requires sealed handle inserts.')
   # Separate 20x20 backing clips behind access opening, not fake painted bolts.
   for k,(x,z) in enumerate(pts):
    clip=box(40,3,40,(x,sign*511.5,z))
    clip=holes(clip,[(x,z)],3.3,axis='Y',start=-600,length=1200)
    add(f'{label}_service_nutclip_{j+1}_{k+1}',clip,'steel','side_service','M6 nut/insert not modeled; clip requires weld detail.')
 # True 3 mm flared lower and tapered upper shoulders, supported by shaped bulkheads.
 # At wheel stations underside is above Z218 mm, nominally >23 mm over provisional shock envelope.
 for sign,label in [(1,'left'),(-1,'right')]:
  for tag,y1,z1,y2,z2 in [('lower',516,220,650,260),('upper',650,260,450,337)]:
   # Plane across Y/Z; define orientation from ordered endpoints to preserve normal thickness.
   dy=y2-y1;dz=z2-z1;ang=math.degrees(math.atan2(dz,sign*dy))
   sh=box(2450,math.hypot(dy,dz),3,(0,0,0)).rotate((0,0,0),(1,0,0),ang).translate((-675,sign*(y1+y2)/2,(z1+z2)/2))
   add('main_'+label+'_'+tag+'_sloping_shoulder',sh,'lid','main_body','Original 3mm planar welded flared shoulder; 1.3m max hull span is a design choice, not a recovered reference dimension.')
 # End walls, with connector openings at the arm-facing forward face.
 for x,label in [(-1898.5,'rear'),(548.5,'arm_facing')]:
  s=cq.Workplane('YZ').polyline([(-513,103),(513,103),(513,220),(650,260),(450,337),(-450,337),(-650,260),(-513,220)]).close().extrude(3).translate((x-1.5,0,0)).val()
  if x>0:s=holes(s,[(-300,235),(300,235)],25,axis='X',start=540,length=20)
  else:s=holes(s,[(0,200)],16,axis='X',start=-1910,length=30)
  add(label+'_bulkhead_3mm',s,'aluminium','main_body','Connector apertures only; glands, EMC seals, bonding and connectors not selected.')
 # Internal segregating bulkheads. Cable routing openings have true B-rep material removal.
 for x,label in [(-1141.5,'controller_battery'),(-458.5,'battery_tool')]:
  s=cq.Workplane('YZ').polyline([(-513,103),(513,103),(513,220),(650,260),(450,337),(-450,337),(-650,260),(-513,220)]).close().extrude(3).translate((x-1.5,0,0)).val()
  s=holes(s,[(300,268)],22,axis='X',start=x-5,length=10)
  s=s.cut(box(10,75,55,(x,440,260)))
  add(label+'_partition',s,'aluminium','main_body','Battery/cable segregation with service openings; fire barrier not qualified.')
 # Recessed welded battery well through the base deck. Corners meet at seams, no overlaps.
 well_floor=plate(650,720,3,-80,-800)
 well_floor=holes(well_floor,[(x,y) for x in (-950,-650) for y in (-235,235)],4.4)
 add('battery_well_floor_3mm',well_floor,'aluminium','battery_well')
 for y,label in [(358.5,'left'),(-358.5,'right')]:
  s=box(650,3,414,(-800,y,130)) # -77..337
  if y>0:s=holes(s,[(-900,268)],22,axis='Y',start=350,length=20)
  add('battery_well_'+label+'_wall',s,'aluminium','battery_well')
 for x,label in [(-1123.5,'rear'),(-476.5,'front')]:
  s=box(3,714,414,(x,0,130))
  add('battery_well_'+label+'_wall',s,'aluminium','battery_well')
 # Exact 4-pack support pads and machined/laser-cut restraints. No battery detail invented.
 for i,(x,y) in enumerate([(x,y) for x in (-950,-650) for y in (-110,110)]):
  add(f'battery_{i+1}_isolator_pad',plate(260,180,4,-77,x,y),'gasket','battery_support','4 mm pad. Battery mass/thermal/chemical compatibility requires supplier validation.')
  # Low lateral stop angles, 10 mm clearance from the dimensional battery envelope.
  for sign in (-1,1):
   yy=y+sign*104
   add(f'battery_{i+1}_stop_{sign}',box(260,3,28,(x,yy,-59)),'restraint','battery_support','Welded low stop; supplier hold-down interface unknown.')
  PROXIES.append({'name':f'DIMENSION_ONLY_RELiON_InSight_48V_battery_{i+1}','shape':box(260,180,276,(x,y,65)),'material':'proxy','mass_kg':15.6,'group':'battery_envelopes','note':'Supplier overall dimensions only; terminal and handle details NOT modeled.'})
 # Top-restraint crossbars intentionally clear nominal envelope by 12 mm. Straps are adjustable concept.
 for i,x in enumerate((-950,-650)):
  s=plate(30,500,4,215,x,0)
  s=holes(s,[(x,-235),(x,235)],4.4)
  add(f'battery_retention_crossbar_{i+1}',s,'restraint','battery_support','12 mm top gap reserved for adjustable insulating pads; clamps NOT contact-qualified.')
  for sy in (-235,235):
   add(f'battery_retention_stud_{i+1}_{sy}',cyl(4,313,(x,sy,-87)),'fastener','battery_support','Smooth M8 tie-rod approximation through real floor/crossbar clearance bores; terminal clearance and preload unresolved.')
   for zz,tag in [(-87,'bottom'),(219,'top')]:
    nut=cq.Workplane('XY').polygon(6,15).circle(4.25).extrude(7).translate((x,sy,zz)).val()
    add(f'battery_retention_nut_{i+1}_{sy}_{tag}',nut,'fastener','battery_support','M8 hex-nut approximation; smooth clearance bore represents omitted threads.')
 # Top deck support ledges, three independent service lids.
 # Rear controller hatch; four controllers/electronics areas do not fill the payload bay.
 hatch('rear_controller_hatch',-1900,-1144,-450,450)
 # Annular shoulder covers the difference between battery well and external body width.
 batt_shoulder=plate(680,900,3,337,-800).cut(plate(650,720,5,336,-800))
 add('battery_deck_shoulder',batt_shoulder,'lid','battery_hatch')
 hatch('battery_hatch',-1125,-475,-360,360,337,'battery_hatch')
 hatch('payload_tool_hatch',-456,550,-450,450,337,'tool_hatch')
 # Two OEM DC controller mounting trays with slotted rails; dimensions-only electronics separate.
 for i,x in enumerate((-1710,-1370)):
  tr=plate(270,550,3,140,x)
  # universal 8x24 slots, deliberately not asserted as vendor bolt pattern
  for xx in (x-105,x+105):
   for yy in (-235,235):tr=tr.cut(cq.Workplane('XY').center(xx,yy).slot2D(24,8,0).extrude(5).translate((0,0,139)).val())
  add(f'controller_mount_tray_{i+1}',tr,'aluminium','controller_trays','Adapter slot locations are our design, not verified against UR OEM hole drawing.')
  for sy in (-250,250):
   # Fold-free built-up L stand-offs, separately modelled weldment plates.
   add(f'controller_tray_leg_{i+1}_{sy}',box(250,3,37,(x,sy,121.5)),'aluminium','controller_trays')
  PROXIES.append({'name':f'DIMENSION_ONLY_UR_OEM_DC_controller_{i+1}','shape':box(168,451,150,(x,0,218)),'material':'proxy','mass_kg':4.3,'group':'controller_envelopes','note':'451×150×168 mm dimensions; source axes rotated so width is Y. No supplier mounting holes or connector detail.'})
 # Segregated cable trough on left (positive Y) side aligns with actual partition openings. 60mm clear width.
 # Tray stays above the rail; interruptions at compartments preserve removable service.
 for i,(xc,ll) in enumerate([(-1518,690),(-800,650),(40,960)]):
  add(f'cable_duct_floor_{i+1}',plate(ll,70,2,230,xc,435),'aluminium','cable_route')
  for yy in (400,470):
   ds=box(ll,2,40,(xc,yy,252))
   if i==1 and yy==400:ds=ds.cut(box(64,8,30,(-900,yy,259)))
   add(f'cable_duct_side_{i+1}_{yy}',ds,'aluminium','cable_route','Open-top duct, branch notch aligned to battery cable aperture; cable/strain-relief selection pending.')
 # Strap clamps pass outside rail Y410..510; no holes in inherited rails.
 for i,(x,sign) in enumerate([(x,s) for x in (-1050,-550) for s in (-1,1)]):
  y=sign*460;pts=[(x,sign*390),(x,sign*530)]
  top=holes(plate(80,160,6,103,x,y),pts,5.4)
  # At inner bolt the base deck already includes a clearance bore.
  add(f'rail_saddle_{i+1}_top',top,'steel','rail_clamps','80×160×6 strap, clamp preload and frame wall crush checks pending.')
  bot=holes(plate(80,160,6,-106,x,y),pts,5.4)
  add(f'rail_saddle_{i+1}_bottom',bot,'steel','rail_clamps')
  for j,(xx,yy) in enumerate(pts):
   screw(f'rail_saddle_{i+1}_M10_{j+1}',xx,yy,109,shaft_len=226,r=5,head_r=8.5,head_h=7,group='rail_clamps')
   nut=cq.Workplane('XY').polygon(6,19.63).circle(5.25).extrude(10).translate((xx,yy,-116)).val()
   add(f'rail_saddle_{i+1}_M10_nut_{j+1}',nut,'fastener','rail_clamps','M10 hex-nut approximation, smooth clearance bore; strength class/preload not selected.')
 # Front tapered tool/nose enclosure, kept clear of both mounting plates.
 # This is a 3mm welded sheet module with sloped crash-deflecting hood, not an impact-rated bumper.
 fb=plate(750,1026,3,100,1575)
 for sy in (-460,460):fb=fb.cut(box(410,144,10,(1350,sy,102)))
 add('front_tool_base',fb,'aluminium','front_tool')
 rw=box(3,1026,194,(1201.5,0,200))
 for sy in (-460,460):rw=rw.cut(box(10,144,32,(1201.5,sy,116)))
 add('front_tool_rear_wall',rw,'aluminium','front_tool')
 # Side plates: XZ plane extrudes -Y. Flat 3mm blanks with actual trapezoid profile.
 poly=[(1203,103),(1947,103),(1947,187),(1700,297),(1203,297)]
 for sign,label in [(1,'left'),(-1,'right')]:
  s=cq.Workplane('XZ').polyline(poly).close().extrude(3).val()
  s=s.translate((0,516 if sign==1 else -513,0))
  s=s.cut(box(410,14,32,(1350,sign*514.5,116)))
  s=s.cut(box(160,32,110,(1350,sign*514.5,160)))
  add('front_tool_'+label+'_side',s,'aluminium','front_tool')
 add('front_tool_nose_wall',box(3,1026,84,(1948.5,0,145)),'aluminium','front_tool')
 # Solid normal-thickness sloped panel between X1700/Z297 and X1947/Z187.
 dx=247;dz=-110;length=math.hypot(dx,dz);ang=math.degrees(math.atan2(-dz,dx))
 slope=box(length,1026,3,(0,0,0)).rotate((0,0,0),(0,1,0),ang).translate(((1700+1947)/2,0,(297+187)/2+1.5))
 add('front_sloped_service_nose',slope,'lid','front_tool','3mm planar sloped sheet; final seam trim and weld detail still required.')
 hatch('front_tool_hatch',1203,1697,-513,513,297,'front_tool')
 # Low removable arm station infill stays below robot mounting contact plane.
 infill=plate(646,200,3,100,875,0)
 add('arm_center_cable_guard',infill,'aluminium','arm_service','Between 400mm arm mounting plates, does not cover UR bolt patterns.')
 # Notch edge guards end before arm pads; nothing is raised above Z130 in the arm station.
 # Chassis-end bumper tubes with real hollow section and cap sheets.
 for x,label in [(-2025,'rear'),(2025,'front')]:
  tube=box(50,1090,70,(x,0,-10)).cut(box(44,1092,64,(x,0,-10)))
  add(label+'_bumper_RHS_70x50x3',tube,'steel','bumpers','Development guard, not crash/tow rated. Attachment brackets must be load-qualified.')
  for sy in (-1,1):
   add(label+f'_bumper_cap_{sy}',box(50,3,70,(x,sy*546.5,-10)),'steel','bumpers')
  for sy in (-460,460):
   # brackets meet frame end plane X±2000 and bumper inner wall X±2000
   bracket=box(30,70,6,(x+(-1 if x>0 else 1)*10,sy,26))
   # Tube inner face meets existing rail end directly. Brackets omitted to avoid unqualified material overlap.


def finish_seams():
 # C02 conservative corner clamp/clevis cutouts. Original panels only, never alter reference frame.
 for p in PARTS:
  for xx in (-1350,0,1350):
   for sy in (-1,1):
    cut=box(480,150,33,(xx,sy*460,115.5)) # Xstation+/-240, |Y|385..535, Z99..132
    pb=p['shape'].BoundingBox();cb=cut.BoundingBox()
    if not (pb.xmax<cb.xmin or pb.xmin>cb.xmax or pb.ymax<cb.ymin or pb.ymin>cb.ymax or pb.zmax<cb.zmin or pb.zmin>cb.zmax):p['shape']=p['shape'].cut(cut)
 # Explicit butt-joint trims at shoulder/side/bulkhead intersections, no hidden material overlaps.
 for p in PARTS:
  if p['name'].endswith('sloping_shoulder'):
   for other in PARTS:
    if (p['name'].endswith('upper_sloping_shoulder') and other['name']==p['name'].replace('upper_sloping','lower_sloping')) or other['name'] in ['main_left_side_3mm','main_right_side_3mm','rear_bulkhead_3mm','arm_facing_bulkhead_3mm','controller_battery_partition','battery_tool_partition']:
     p['shape']=p['shape'].cut(other['shape'])
   p['note']+=' Edge mitres and bulkhead notches explicitly trimmed in B-rep.'

def bounds(s):
 from OCP.Bnd import Bnd_Box
 from OCP.BRepBndLib import BRepBndLib
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return list(b.Get())
def export_glb(parts,path):
 data=bytearray();views=[];acc=[];meshes=[];nodes=[];mat_names=list(MATS)
 def buf(a,typ,comp):
  a=np.asarray(a,dtype=np.float32 if comp==5126 else np.uint32)
  data.extend(b'\0'*((-len(data))%4));off=len(data);data.extend(a.tobytes());vi=len(views);views.append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes});idx=len(acc)
  ac={'bufferView':vi,'componentType':comp,'count':len(a),'type':typ}
  if typ=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  acc.append(ac);return idx
 for p in parts:
  s=p['shape'];verts,tris=s.tessellate(.35,.12);v=np.array([[q.x,q.y,q.z] for q in verts])/1000;f=np.asarray(tris,np.uint32);v=v[f].reshape(-1,3)
  no=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);no=np.repeat(no,3,axis=0)
  pi=buf(v,'VEC3',5126);ni=buf(no,'VEC3',5126);ii=buf(np.arange(len(v),dtype=np.uint32),'SCALAR',5125)
  meshes.append({'name':p['name'],'primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni},'indices':ii,'material':mat_names.index(p['material'])}]})
  nodes.append({'name':p['name'],'mesh':len(meshes)-1,'extras':{'classification':'dimensional_reservation' if p['material']=='proxy' else 'original_engineering_CAD','group':p['group'],'note':p['note']}})
 mats=[{'name':k,'pbrMetallicRoughness':{'baseColorFactor':v['color'],'metallicFactor':0 if k in ['gasket','proxy'] else .45,'roughnessFactor':.6},**({'alphaMode':'BLEND','doubleSided':True} if k=='proxy' else {})} for k,v in MATS.items()]
 doc={'asset':{'version':'2.0','generator':'Original body-power R01, CadQuery B-rep tessellation; metres Z-up'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':acc,'extras':{'units':'metres','upAxis':'Z','qualified':False,'classification':'dimensional_reservations_only' if parts is PROXIES else 'original_manufacturing_development_CAD'}}
 js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4)
 path.write_bytes(struct.pack('<III',0x46546C67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(data),0x004E4942)+data)

def verify():
 bs=[bounds(p['shape']) for p in PARTS];inter=[];contacts=[]
 for i,a in enumerate(PARTS):
  for j in range(i+1,len(PARTS)):
   b=PARTS[j]
   if any(bs[i][k+3]<bs[j][k]-1e-5 or bs[j][k+3]<bs[i][k]-1e-5 for k in range(3)):continue
   vol=a['shape'].intersect(b['shape']).Volume()
   if vol>1e-3:inter.append({'a':a['name'],'b':b['name'],'volume_mm3':vol})
   elif a['shape'].distance(b['shape'])<1e-5:contacts.append([a['name'],b['name']])
 frame=cq.importers.importStep(str(REFERENCE_FRAME)).val()
 frame_inter=[]
 for p in PARTS:
  b=bounds(p['shape'])
  if b[2]>.131e3 or b[5]<-100.001:continue
  vol=p['shape'].intersect(frame).Volume()
  if vol>1e-3:frame_inter.append({'part':p['name'],'volume_mm3':vol})
 props=[]
 for p in PARTS:
  s=p['shape'];c=s.Center();mass=s.Volume()*1e-9*MATS[p['material']]['density']
  props.append({'name':p['name'],'group':p['group'],'material':p['material'],'valid':s.isValid(),'solid_count':len(s.Solids()),'mass_kg':mass,'volume_m3':s.Volume()*1e-9,'com_m':[c.x/1000,c.y/1000,c.z/1000],'bounds_m':(np.asarray(bounds(s))/1000).tolist(),'note':p['note']})
 mass=sum(p['mass_kg'] for p in props);cg=(sum((np.asarray(p['com_m'])*p['mass_kg'] for p in props),np.zeros(3))/mass).tolist()
 overall=np.vstack(bs);bnd=[overall[:,:3].min(axis=0).tolist(),overall[:,3:].max(axis=0).tolist()]
 proxyprops=[];proxycoll=[]
 for q in PROXIES:
  c=q['shape'].Center();proxyprops.append({'name':q['name'],'mass_kg':q['mass_kg'],'com_m':[c.x/1000,c.y/1000,c.z/1000],'bounds_m':(np.asarray(bounds(q['shape']))/1000).tolist(),'note':q['note']})
  for p in PARTS:
   vol=q['shape'].intersect(p['shape']).Volume() if all(bounds(q['shape'])[k]<bounds(p['shape'])[k+3] and bounds(p['shape'])[k]<bounds(q['shape'])[k+3] for k in range(3)) else 0
   if vol>1e-3:proxycoll.append({'proxy':q['name'],'part':p['name'],'volume_mm3':vol})
 loaded_mass=mass+sum(q['mass_kg'] for q in proxyprops);loaded_cg=(np.asarray(cg)*mass+sum((np.asarray(q['com_m'])*q['mass_kg'] for q in proxyprops),np.zeros(3)))/loaded_mass
 report={'revision':'R01','release_status':'manufacturing-development, not fabrication/operational release','units':{'CAD':'mm','GLB':'m, Z-up'},'original_part_count':len(PARTS),'individual_valid':all(p['valid'] for p in props),'bounds_m':(np.asarray(bnd)/1000).tolist(),'material_assumptions':MATS,'body_hardware_mass_kg':mass,'body_hardware_com_m':cg,'body_plus_reserved_component_mass_kg':loaded_mass,'body_plus_reserved_component_com_m':loaded_cg.tolist(),'positive_volume_body_intersections':inter,'frame_intersections':frame_inter,'dimensional_reservation_intersections':proxycoll,'zero_gap_contacts':contacts,'parts':props,'dimensional_reservations':proxyprops,'exclusions':['frame mass, arms, drive train, wheels, tools, cabling, cooling fans, glands and fastener threads excluded from this package mass','OEM controller mass allocated uniformly at dimensional-envelope centroid, not measured supplier CG','battery mass allocated uniformly at supplier-envelope centroid, not measured supplier CG','mounting/welding/contact validation is geometrical only; no strength, fatigue, stability or IP qualification']}
 (P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['parts','zero_gap_contacts','material_assumptions','dimensional_reservations']},indent=2),flush=True)
 return report

def main():
 build();finish_seams();print('built',len(PARTS),'parts',flush=True)
 r=verify()
 for parts,stem in [(PARTS,'body_power_R01'),(PROXIES,'cots_reservations_R01')]:
  ass=cq.Assembly(name=stem)
  for p in parts:ass.add(p['shape'],name=p['name'],color=cq.Color(*MATS[p['material']]['color']))
  ass.export(str(P/(stem+'.step')));export_glb(parts,P/(stem+'.glb'));print('exported',stem,flush=True)
 with (P/'original_cutlist.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['part','group','material_assumption','mass_kg','bounds_mm','note'])
  for p in r['parts']:w.writerow([p['name'],p['group'],MATS[p['material']]['assumption'],p['mass_kg'],json.dumps((np.asarray(p['bounds_m'])*1000).tolist()),p['note']])
 if r['positive_volume_body_intersections'] or r['frame_intersections'] or r['dimensional_reservation_intersections']:print('FIX INTERSECTIONS BEFORE RELEASE',flush=True)
if __name__=='__main__':main()
