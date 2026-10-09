"""Original source-backed fit-development wheel C01. Not OEM CAD or a manufacturing drawing.
CadQuery B-rep uses mm, X forward, Y axle/outboard, Z up. GLB uses metres, same axes.
Published major dimensions only; cross-section, tread and disc are original assumptions.
Run: python build_wheel.py. CadQuery 2.7.0 / OCP 7.8.1 / numpy.
"""
from pathlib import Path
import cadquery as cq
import numpy as np
import json, math, struct, hashlib, time
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent
PARAM={
 'tire_diameter_mm':876.3,'tire_section_width_mm':317.5,'tire_measuring_rim_width_mm':254.,
 'tread_depth_mm':18/32*25.4,'bead_seat_diameter_mm':18*25.4,'bead_seat_width_mm':8.5*25.4,
 'rim_pcd_mm':165.1,'rim_hole_count':5,'center_bore_mm':114.1,'offset_mm':18.,'lug_phase_deg':36.,
 'assumed_lug_hole_mm':18.,'assumed_hub_pad_thickness_mm':20.,
 'assumed_barrel_wall_mm':8.,'assumed_flange_height_mm':16.,'assumed_flange_thickness_mm':7.,
 'assumed_tread_rows':4,'assumed_tread_repeats':40,'assumed_tread_arc_deg':6.3,
 'assumed_tread_row_width_mm':46.,'assumed_tread_row_centers_mm':[-82.5,-27.5,27.5,82.5],
 'assumed_vent_count':5,'assumed_vent_pcd_mm':308.,'assumed_vent_diameter_mm':72.,
}
COLORS={'tire':[.075,.083,.085,1.],'rim':[.45,.50,.52,1.]}
def rev(poly):return cq.Workplane('XY').polyline(poly).close().revolve(360,(0,0),(0,1)).val()
def cyl_y(r,y0,y1,x=0,z=0):return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False)
 return list(b.Get())
def bez(a,b,c,d,n=14):
 a,b,c,d=map(np.asarray,(a,b,c,d))
 return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in np.linspace(0,1,n+1)]
def tire_profile():
 # Right-hand profile in (radius,axialY). Interior cavity is open to the rim.
 # All shape values except outer extrema, nominal bead diameter/width are assumptions.
 bead=PARAM['bead_seat_diameter_mm']/2;h=PARAM['bead_seat_width_mm']/2
 R=PARAM['tire_diameter_mm']/2;root=R-PARAM['tread_depth_mm'];w=PARAM['tire_section_width_mm']/2
 outer=[(bead,90),(bead,h),(bead+16,h),(bead+25,h+11)]
 outer+=bez(outer[-1],(278,137),(316,w),(345,w))[1:]
 outer+=bez(outer[-1],(387,w),(root,140),(root,112))[1:]
 # Outer goes right bead->right shoulder->crown->left shoulder->left bead.
 full=outer+[(r,-y) for r,y in reversed(outer)]
 # Carcass inner cavity, conservative geometric assumption, no ply/cord simulation.
 inner_r=[(bead,90),(250,91),(274,114),(314,132),(345,140),
          (382,135),(402,117),(410,94),(410,0)]
 full += [(r,-y) for r,y in inner_r[1:]]
 full += list(reversed(inner_r[:-1]))
 return full

def tread_sector(ycenter,phase):
 # Original generic block. Never traced from the KM3 tread. Annular sector gives exact OD.
 r0=PARAM['tire_diameter_mm']/2-PARAM['tread_depth_mm']-1
 r1=PARAM['tire_diameter_mm']/2
 a=math.radians(PARAM['assumed_tread_arc_deg']/2)
 def pt(r,t):return (r*math.cos(t),r*math.sin(t))
 # XZ workplane extrudes along -Y; translate to center on row.
 s=(cq.Workplane('XZ').moveTo(*pt(r0,-a)).lineTo(*pt(r1,-a))
    .threePointArc(pt(r1,0),pt(r1,a)).lineTo(*pt(r0,a))
    .threePointArc(pt(r0,0),pt(r0,-a)).close().extrude(PARAM['assumed_tread_row_width_mm']).val())
 return s.translate((0,ycenter+PARAM['assumed_tread_row_width_mm']/2,0)).rotate((0,0,0),(0,1,0),phase)

def build_tire():
 carcass=rev(tire_profile())
 # Single fused tire solid. 160 original blocks, no copied logos/sidewall lettering.
 blocks=[]
 for row,y in enumerate(PARAM['assumed_tread_row_centers_mm']):
  phase=0 if row in (0,3) else 4.5
  template=tread_sector(y,phase)
  for i in range(PARAM['assumed_tread_repeats']):blocks.append(template.rotate((0,0,0),(0,1,0),i*9))
 print('Fusing tire carcass and',len(blocks),'original tread blocks',flush=True)
 tire=carcass.fuse(*blocks).clean()
 return tire,carcass,blocks

def build_rim():
 r=PARAM['bead_seat_diameter_mm']/2;h=PARAM['bead_seat_width_mm']/2
 # Nominal 18in bead-seat diameter and 8.5in width. Dropwell, hump, flange details assumed.
 outer=[(r+16,-h-7),(r+16,-h),(r,-h),(r,-90),(r+1.5,-84),
        (r-5,-74),(r-23,-40),(r-23,40),(r-5,74),(r+1.5,84),
        (r,90),(r,h),(r+16,h),(r+16,h+7)]
 inner=[(r-8,h+7),(r-8,90),(r-7,84),(r-13,74),(r-31,40),
        (r-31,-40),(r-13,-74),(r-7,-84),(r-8,-90),(r-8,-h-7)]
 barrel=rev(outer+inner)
 # Original perforated dish, intentionally does not recreate EVO's paired-spoke appearance.
 # The mounting face is exactly +18mm from the center plane. Flat washer seats at +38mm.
 hub=cyl_y(109,18,38).cut(cyl_y(PARAM['center_bore_mm']/2,17,39))
 dish=rev([(102,18),(112,18),(225,76),(225,87),(212,84),(104,38),(102,38)])
 rim=barrel.fuse(hub,dish).clean()
 lug_centers=[]
 for i in range(5):
  a=2*math.pi*i/5+math.radians(PARAM['lug_phase_deg']); x=PARAM['rim_pcd_mm']/2*math.cos(a);z=PARAM['rim_pcd_mm']/2*math.sin(a)
  lug_centers.append([x,18,z]);rim=rim.cut(cyl_y(PARAM['assumed_lug_hole_mm']/2,-120,120,x,z))
 for i in range(5):
  a=2*math.pi*(i+.5)/5+math.radians(PARAM['lug_phase_deg']);x=154*math.cos(a);z=154*math.sin(a)
  rim=rim.cut(cyl_y(36,-120,120,x,z))
 return rim.clean(),barrel,lug_centers

def export_glb(parts,path):
 data=bytearray();views=[];acc=[];meshes=[];nodes=[];stats={}
 def buf(a,typ,comp):
  a=np.asarray(a,dtype=np.float32 if comp==5126 else np.uint32)
  data.extend(b'\0'*((-len(data))%4));off=len(data);data.extend(a.tobytes());vi=len(views)
  views.append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes});idx=len(acc)
  ac={'bufferView':vi,'componentType':comp,'count':len(a),'type':typ}
  if typ=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  acc.append(ac);return idx
 for i,(name,s) in enumerate(parts.items()):
  vv,ff=s.tessellate(.30,.07)
  original=np.array([[q.x,q.y,q.z] for q in vv])/1000
  f=np.asarray(ff,np.uint32);v=original[f].reshape(-1,3)
  n=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);n=np.repeat(n,3,axis=0)
  pi=buf(v,'VEC3',5126);ni=buf(n,'VEC3',5126);ii=buf(np.arange(len(v),dtype=np.uint32),'SCALAR',5125)
  meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni},'indices':ii,'material':i}]})
  nodes.append({'name':name,'mesh':i,'extras':{'classification':'original_source_backed_parametric_fit_model','oemCAD':False,'assumptions':True}})
  stats[name]={'vertices':len(v),'triangles':len(f),'bounds_m':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]}
 materials=[{'name':name,'pbrMetallicRoughness':{'baseColorFactor':COLORS[name],'metallicFactor':0 if name=='tire' else .7,'roughnessFactor':.90 if name=='tire' else .55}} for name in parts]
 doc={'asset':{'version':'2.0','generator':'Original CQ tire/rim C01, mm B-rep to metre tessellation'},'scene':0,
 'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':materials,
 'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':acc,
 'extras':{'units':'metres','upAxis':'Z','axleAxis':'+Y','origin':'wheel center','oemCAD':False,'qualified':False,
 'classification':'original source-backed dimensional fit model','warning':'Z-up engineering asset: consumers must preserve explicit coordinate contract; native glTF convention is Y-up.'}}
 js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4)
 path.write_bytes(struct.pack('<III',0x46546C67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(data),0x004E4942)+data)
 return stats

def main():
 start=time.time();(P/'parameters.json').write_text(json.dumps(PARAM,indent=2)+'\n')
 tire,carcass,blocks=build_tire();rim,barrel,lugs=build_rim()
 parts={'tire':tire,'rim':rim}
 for name,s in parts.items():
  print(name,'valid',s.isValid(),'solids',len(s.Solids()),'bounds',bounds(s),'volume',s.Volume(),flush=True)
  assert s.isValid() and len(s.Solids())==1,name
 ass=cq.Assembly(name='original_source_backed_wheel_C01')
 for name,s in parts.items():ass.add(s,name=name,color=cq.Color(*COLORS[name]))
 ass.export(str(P/'wheel_C01.step'))
 cq.exporters.export(tire,str(P/'tire_C01.step'));cq.exporters.export(rim,str(P/'rim_C01.step'))
 stats=export_glb(parts,P/'wheel_C01.glb')
 clash=tire.intersect(rim).Volume();print('Tire rim intersection mm3',clash,flush=True)
 # Exact point-based interface test avoids claiming that undeclared dimensions are OEM facts.
 tests={
 'all_brep_parts_valid':all(s.isValid() for s in parts.values()),
 'two_single_solid_parts':all(len(s.Solids())==1 for s in parts.values()),
 'tire_rim_no_volume_overlap':abs(clash)<1e-4,
 'outer_diameter_x_matches876_3':abs((bounds(tire)[3]-bounds(tire)[0])-876.3)<1e-5,
 'outer_diameter_z_matches876_3':abs((bounds(tire)[5]-bounds(tire)[2])-876.3)<1e-5,
 'section_width_matches_provisional317_5':abs((bounds(tire)[4]-bounds(tire)[1])-317.5)<1e-5,
 'five_lug_through_holes':all(not rim.isInside(cq.Vector(x,28,z),1e-6) for x,y,z in lugs),
 'center_bore_open':all(not rim.isInside(cq.Vector(56.5,yy,0),1e-6) for yy in (18.1,28,37.9)),
 'center_bore_wall_present':rim.isInside(cq.Vector(58,28,0),1e-6),
 'flat_mounting_pad_material':rim.isInside(cq.Vector(67,18.01,0),1e-6) and not rim.isInside(cq.Vector(67,17.99,0),1e-6),
 'inner_air_cavity_open':not tire.isInside(cq.Vector(350,0,0),1e-6),
 'bead_nominal_contact':tire.isInside(cq.Vector(228.61,100,0),1e-6) and barrel.isInside(cq.Vector(228.59,100,0),1e-6),
 }
 verification={'revision':'C01','cadquery':cq.__version__,'elapsed_s':time.time()-start,'tests':tests,
 'brep_bounds_mm':{n:bounds(s) for n,s in parts.items()},'volume_mm3':{n:s.Volume() for n,s in parts.items()},
 'triangle_mesh':stats,'tire_rim_overlap_mm3':clash,'qualified':False,
 'limitations':['These tests verify this original model, not actual OEM geometry or physical fit.',
 'Tire envelope on 8.5in rim is provisional; manufacturer measuring rim is 10in.',
 'No structural, fatigue, pressure, bead-retention, fastener, offset-load, brake, or vehicle qualification.',
 'No manufacturer CAD used or claimed. Generic original tread and wheel disc.']}
 (P/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
 iface={'revision':'C01','asset':'wheel_C01.glb','native_cad':'build_wheel.py','step':'wheel_C01.step',
 'units':{'native_and_step':'millimetres','glb':'metres'},'axes':{'X':'forward','Y':'axle / outboard','Z':'up'},
 'origin':'tire and bead-seat center plane at axle','nominal_radius_m':.43815,
 'provisional_section_width_m':.3175,'tire_width_measuring_rim_m':.254,'actual_width_on_selected_rim_verified':False,
 'mount_face_center_m':[0,.018,0],'mount_face_outboard_normal':[0,1,0],
 'assembly_contact_normal_toward_adapter':[0,-1,0],'bead_seat_diameter_m':.4572,'bead_seat_width_m':.2159,
 'rim_pcd_m':.1651,'rim_hole_count':5,'lug_phase_deg':36.,'lug_phase_convention':'angle in XZ plane from +X toward +Z','rim_bore_diameter_m':.1141,
 'lug_centers_mount_face_m':[[v/1000 for v in p] for p in lugs],
 'assumed_hole_diameter_m':.018,'assumed_hub_pad_thickness_m':.020,'nut_seat':'published flat; washer seat at assumed y=.038m',
 'matching_nut_spec':'EVO CM0750180040, M16x1.5 flat washer seat; final stud engagement unverified',
 'drive_adapter_required':True,'drive_pattern_m':{'pcd':.140,'pilot':.094,'holes':5},
 'left_instance_transform':'translation only from local center; +Y is outboard',
 'right_instance_transform':'Rz(180 degrees) then translation; determinant +1; no negative scale',
 'do_not_scale':True,'separate_mesh_nodes':['tire','rim'],
 'manufacturer_CAD':False,'fit_or_manufacture_approved':False,
 'sourced_load_notes':{'tire_single_lb_at_psi':[3415,75],'rim_catalog_kg':1400,'applies_to_this_original_model':False},
 'bounds_m':stats,'source_file':'SOURCES.json','assumptions_file':'ASSUMPTIONS.md'}
 (P/'interface_contract.json').write_text(json.dumps(iface,indent=2)+'\n')
 print('TESTS',tests,flush=True)
 assert all(tests.values()),'Verification failure: see verification.json'
 # Hash only deliverables; recompute after documentation via write_hashes.py.
 print('Completed',time.time()-start,'seconds',flush=True)
if __name__=='__main__':main()
