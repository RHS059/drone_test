"""Original static workholding concepts S01, mm and vehicle X/Y/Z-up.
Not lifting equipment; no assigned safe working load; no fabrication release.
Generates only original geometry. It never imports proprietary drive geometry.
"""
from pathlib import Path
import cadquery as cq
import numpy as np
import json, math, struct, csv, hashlib
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent
PARAM={"revision":"S01","frame_revision":"R07","corner_revision":"C02_R05","rail_centers_Y_mm":[-460,460],"support_stations_X_mm":[-1775,1775],"rail_bottom_Z_mm":-100,"service_raise_mm":100,"nominal_tire_ground_Z_mm":-688.15,"service_floor_Z_mm":-788.15,"tire_radius_mm":438.15,"tire_section_width_mm":317.5,"wheel_center_mm":[0,940,-250],"assumed_steel_density_kg_m3":7850,"assumed_elastomer_density_kg_m3":1200}
PARTS=[]
def box(a,b,c,xyz):return cq.Workplane('XY').box(a,b,c).translate(xyz).val()
def cyl(r,L,p,v=(0,0,1),ri=0):
 w=cq.Workplane(cq.Plane(origin=p,normal=v)).circle(r)
 if ri:w=w.circle(ri)
 return w.extrude(L).val()
def hexagon(af,L,p,v=(0,0,1),hole=None):
 w=cq.Workplane(cq.Plane(origin=p,normal=v)).polygon(6,af/math.cos(math.pi/6))
 if hole:w=w.circle(hole)
 return w.extrude(L).val()
def rhs(axis,L,w,h,t,c):
 d=(L,w,h) if axis=='X' else (w,L,h) if axis=='Y' else (w,h,L)
 inner=(L+2,w-2*t,h-2*t) if axis=='X' else (w-2*t,L+2,h-2*t) if axis=='Y' else (w-2*t,h-2*t,L+2)
 # Explicit square-corner plate-built hollow section; not represented as mill stock.
 return box(*d,c).cut(box(*inner,c))
def add(name,shape,group,material='steel',note=''):
 assert shape.isValid() and len(shape.Solids())==1, name
 PARTS.append(dict(name=name,shape=shape,group=group,material=material,note=note));return shape

def trestles():
 floor=PARAM['service_floor_Z_mm'];foot_top=floor+16
 for i,x in enumerate(PARAM['support_stations_X_mm']):
  pre=f'trestle_{i+1}'
  add(pre+'_transverse_box_200x100x6',rhs('Y',1300,200,100,6,(x,0,-166)),'chassis_support',note='Original plate-built closed section; welds and section strength not qualified.')
  for side,y in [('left',460),('right',-460)]:
   q=pre+'_'+side
   foot=box(350,350,16,(x,y,floor+8))
   for dx in [-130,130]:
    for dy in [-130,130]:foot=foot.cut(cyl(9,18,(x+dx,y+dy,floor-1)))
   add(q+'_foot_plate',foot,'chassis_support',note='Four Ø18 optional engineered floor-anchor holes. No anchor or slab capacity selected; not asserted anchored.')
   postL=-216-foot_top
   add(q+'_post_box_100x100x6',rhs('Z',postL,100,100,6,(x,y,(foot_top-216)/2)),'chassis_support')
   add(q+'_rail_bearing_pad',box(160,220,16,(x,y,-108)),'chassis_support',note='Top face Z−100 bears directly on R07 bottom rail flats. Welded to crossbeam; no lifting point.')
   for sg in [-1,1]:
    cy=y+sg*61
    cheek=box(140,6,70,(x,cy,-65))
    for dx in [-45,45]:cheek=cheek.cut(cyl(6.5,10,(x+dx,cy-5,-55),(0,1,0)))
    add(q+f'_locator_cheek_{sg}',cheek,'chassis_support',note='8 mm clear of nominal rail side; locates only, not the gravity load path.')
    for j,dx in enumerate([-45,45]):
     # Boss outside cheek: selected finished M12 thread still to be specified.
     n=q+f'_locator_{sg}_{j+1}'
     boss=cyl(12,14,(x+dx,y+sg*64,-55),(0,sg,0),6.5)
     add(n+'_thread_boss',boss,'chassis_support',note='Smooth Ø13 bore represents omitted thread detail. M12 mating thread/engagement and weld must be designed before use.')
     shaft=cyl(6,38,(x+dx,y+sg*54,-55),(0,sg,0))
     head=hexagon(18,8,(x+dx,y+sg*92,-55),(0,sg,0))
     puck=cyl(9,4,(x+dx,y+sg*50,-55),(0,sg,0))
     add(n+'_screw_and_flat_tip',shaft.fuse(head).fuse(puck),'fastener',note='Original smooth-shank nominal M12 locator. Rail side contact at ±50 mm. Do not use clamp friction for suspension, uplift, or rated restraint.')


def cradle():
 floor=PARAM['service_floor_Z_mm'];top=floor+16;R=PARAM['tire_radius_mm'];yc=940;zc=-250
 for y in [720,1160]:
  for x in [-480,480]:
   f=box(160,160,16,(x,y,floor+8))
   for dx in [-50,50]:
    for dy in [-50,50]:f=f.cut(cyl(8.5,18,(x+dx,y+dy,floor-1)))
   add(f'cradle_foot_{x}_{y}',f,'corner_cradle',note='Floor contact, no casters. Anchor pattern is original and unqualified.')
  rail=rhs('X',1120,80,80,5,(0,y,top+40))
  for xx in [-375,-305,305,375]:rail=rail.cut(cyl(5.5,8,(xx,y,top+74)))
  add(f'cradle_longitudinal_box_{y}',rail,'corner_cradle')
 for x in [-220,220]:
  add(f'cradle_cross_box_{x}',rhs('Y',360,100,40,5,(x,940,top+20)),'corner_cradle')
  # Solid machined/laminated contour shoe. Its analytical circle is the stated tire envelope,
  # not a copied supplier tire mesh. Width covers the original four tread rows.
  blk=box(240,240,252.15,(x,940,(-732.15-480)/2))
  outer=cyl(R+6,500,(0,690,zc),(0,1,0))
  inner=cyl(R,502,(0,689,zc),(0,1,0))
  void=box(224,224,244.15,(x,940,(-724.15-480)/2)).cut(cyl(R+12,500,(0,690,zc),(0,1,0)))
  add(f'cradle_contour_shoe_{x}',blk.cut(outer).cut(void),'corner_cradle',note='Original closed weldment: 8 mm bottom/end/side walls and 6 mm curved top, concave R444.15. Bottom rests on crossmember Z−732.15. Weld design and strength not released.')
  add(f'cradle_replaceable_contact_liner_{x}',blk.intersect(outer).cut(inner),'corner_cradle','elastomer','6 mm radial nominal liner follows R438.15 unloaded tire envelope. Real tread compression/contact, width on 8.5-in rim and liner attachment remain qualification gates.')
 # Two bolted overhead crossbars close the cradle. They limit gross escape but are not rated restraints.
 for x in [-340,340]:
  for y in [720,1160]:
   postbottom=top+88;posttop=88
   base=box(100,70,8,(x,y,top+84))
   for dx in [-35,35]:
    xx=x+dx;base=base.cut(cyl(5.5,10,(xx,y,top+79)))
    add(f'cradle_post_base_weldnut_{x}_{y}_{dx}',hexagon(17,10,(xx,y,top+65),hole=5.5),'fastener',note='Retained beneath top rail wall; nominal smooth-bore M10 envelope, no thread or weld rating.')
    add(f'cradle_post_base_washer_{x}_{y}_{dx}',cyl(10,2,(xx,y,top+88),ri=5.5),'fastener')
    add(f'cradle_post_base_bolt_{x}_{y}_{dx}',cyl(5,25,(xx,y,top+65)).fuse(hexagon(17,7,(xx,y,top+90))),'fastener',note='Remove to install capture-post weldment after unloaded cradle is positioned beneath supported corner.')
   add(f'cradle_capture_post_base_{x}_{y}',base,'corner_cradle',note='Removable post weldment: two M10-style through fasteners into retained rail nuts; structural approval required.')
   add(f'cradle_capture_post_{x}_{y}',rhs('Z',posttop-postbottom,40,40,3,(x,y,(postbottom+posttop)/2)),'corner_cradle')
   cap=box(60,60,12,(x,y,94)).cut(cyl(6.5,14,(x,y,87)))
   add(f'cradle_capture_post_cap_{x}_{y}',cap,'corner_cradle')
   add(f'cradle_capture_weldnut_{x}_{y}',hexagon(18,10,(x,y,78),hole=6.5),'fastener',note='Nominal captive weldnut, threads omitted. No proof of weld or fastener capacity.')
   add(f'cradle_capture_washer_{x}_{y}',cyl(12,2,(x,y,140),ri=6.5),'fastener')
   bolt=cyl(6,64,(x,y,78)).fuse(hexagon(18,8,(x,y,142)))
   add(f'cradle_capture_bolt_{x}_{y}',bolt,'fastener',note='Original M12-style smooth-shank captive crossbar fastener, length/grade/preload not selected.')
  bridge=rhs('Y',480,40,40,3,(x,940,120))
  for y in [720,1160]:bridge=bridge.cut(cyl(6.5,44,(x,y,98)))
  add(f'cradle_removable_capture_crossbar_{x}',bridge,'corner_cradle',note='Install after supported module is seated. This closes the cage; it is not a lifting bail or approved transport restraint.')


def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return list(b.Get())
def overlaps(a,b,tol=1e-5):
 return all(a[k+3]>=b[k]-tol and b[k+3]>=a[k]-tol for k in range(3))
def glb(parts,path):
 data=bytearray();views=[];acc=[];meshes=[];nodes=[]
 mats={'steel':[.78,.46,.10,1],'fastener':[.50,.54,.57,1],'elastomer':[.07,.08,.085,1]}
 def buf(a,typ,component):
  a=np.asarray(a,dtype=np.float32 if component==5126 else np.uint32);data.extend(b'\0'*(-len(data)%4));off=len(data);data.extend(a.tobytes());vi=len(views);views.append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes});ac={'bufferView':vi,'componentType':component,'count':len(a),'type':typ}
  if typ=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  acc.append(ac);return len(acc)-1
 for p in parts:
  vv,ff=p['shape'].tessellate(.3,.15);v=np.array([[a.x,a.y,a.z]for a in vv])/1000;v=v[np.asarray(ff,np.uint32)].reshape(-1,3);n=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);n=np.repeat(n,3,axis=0)
  pi=buf(v,'VEC3',5126);ni=buf(n,'VEC3',5126);ii=buf(np.arange(len(v)),'SCALAR',5125)
  meshes.append({'name':p['name'],'primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni},'indices':ii,'material':list(mats).index(p['material'])}]});nodes.append({'name':p['name'],'mesh':len(meshes)-1,'extras':{'classification':'original_unqualified_static_workholding','group':p['group'],'note':p['note']}})
 doc={'asset':{'version':'2.0','generator':'Original S01 CadQuery workholding, no manufacturer fixture geometry'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':[{'name':k,'pbrMetallicRoughness':{'baseColorFactor':c,'metallicFactor':0 if k=='elastomer' else .45,'roughnessFactor':.6}}for k,c in mats.items()],'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':acc,'extras':{'units':'metres','upAxis':'Z','fabrication_release':False,'rated_load_kg':None,'not_lifting_equipment':True}}
 js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*(-len(js)%4);data+=b'\0'*(-len(data)%4);path.write_bytes(struct.pack('<III',0x46546C67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(data),0x004E4942)+data)

def export(parts,stem):
 ass=cq.Assembly(name=stem)
 for p in parts:ass.add(p['shape'],name=p['name'])
 ass.export(str(P/(stem+'.step')));glb(parts,P/(stem+'.glb'))
 props=[];clash=[];contacts=[];bs=[bounds(p['shape'])for p in parts]
 for i,a in enumerate(parts):
  vol=a['shape'].Volume();rho=1200 if a['material']=='elastomer' else 7850
  props.append({k:v for k,v in a.items()if k!='shape'}|{'volume_mm3':vol,'assumed_mass_kg':vol*rho*1e-9,'bounds_mm':bs[i],'BRep_valid':a['shape'].isValid(),'solid_count':len(a['shape'].Solids())})
  for j in range(i+1,len(parts)):
   if not overlaps(bs[i],bs[j]):continue
   v=a['shape'].intersect(parts[j]['shape']).Volume()
   if v>1e-3:clash.append([a['name'],parts[j]['name'],v])
   elif a['shape'].distance(parts[j]['shape'])<1e-5:contacts.append([a['name'],parts[j]['name']])
 report={'revision':stem,'parts':props,'count':len(parts),'all_single_valid_solids':all(p['BRep_valid']and p['solid_count']==1 for p in props),'total_assumed_mass_kg':sum(p['assumed_mass_kg']for p in props),'positive_volume_intersections_mm3':clash,'zero_gap_contacts':contacts,'fabrication_release':False,'rated_load_kg':None,'source_safety_class':'original static workholding development only'}
 (P/(stem+'_verification.json')).write_text(json.dumps(report,indent=2));print(stem,'parts',len(parts),'clashes',clash,'mass',report['total_assumed_mass_kg'],flush=True)
 return report
if __name__=='__main__':
 trestles();nt=len(PARTS);cradle()
 (P/'parameters.json').write_text(json.dumps(PARAM,indent=2))
 a=export(PARTS[:nt],'chassis_trestles_S01');b=export(PARTS[nt:],'corner_cradle_S01')
 glb(PARTS,P/'service_fixtures_S01.glb')
 with(P/'parts_S01.csv').open('w')as f:
  w=csv.writer(f);w.writerow(['part','group','material_assumption','volume_mm3','mass_kg','note'])
  for p in a['parts']+b['parts']:w.writerow([p['name'],p['group'],p['material'],p['volume_mm3'],p['assumed_mass_kg'],p['note']])
 assert not a['positive_volume_intersections_mm3'] and not b['positive_volume_intersections_mm3']
