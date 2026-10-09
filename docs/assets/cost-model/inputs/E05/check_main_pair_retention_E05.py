"""Supplement actual exported E05 retention and conservative scenario evidence."""
from pathlib import Path
import cadquery as cq,json,struct,hashlib,math
P=Path(__file__).resolve().parent;O=P/'main_routes_E05'
C=json.loads((O/'main_pair_contract_E05.json').read_text());G=json.loads((O/'main_pair_geometry_check_E05.json').read_text())
b=(O/'main_pair_supported_E05.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);ss=list(cq.importers.importStep(str(O/'main_pair_supported_E05.step')).val());new=dict(zip([n['name']for n in j['nodes']],ss))
checks=[]
def shared_area(x,y):
 total=0.
 for a in x.Faces():
  aa=a.BoundingBox()
  for b in y.Faces():
   bb=b.BoundingBox()
   if aa.xmin>bb.xmax+1e-5 or bb.xmin>aa.xmax+1e-5 or aa.ymin>bb.ymax+1e-5 or bb.ymin>aa.ymax+1e-5 or aa.zmin>bb.zmax+1e-5 or bb.zmin>aa.zmax+1e-5:continue
   if a.distance(b)<1e-5:total+=a.intersect(b).Area()
 return total
def contact(a,b):
 x,y=new[a],new[b];return {'from':a,'to':b,'gap_mm':x.distance(y),'shared_surface_area_mm2':shared_area(x,y)}
for s in C['supports']:
 n=s['id'];row={'support':n,'contacts':[]}
 for i in [0,1]:
  for a,b in [('M4x30','upper_washer'),('lower_washer','M4nut')]:row['contacts'].append(contact(n+f'_{a}_{i}',n+f'_{b}_{i}'))
  row['contacts'].append(contact(n+f'_upper_washer_{i}',n+'_upper_clamp'));row['contacts'].append(contact(n+f'_lower_washer_{i}',n+'_welded_stand'))
 row['pass']=all(p['gap_mm']<1e-4 and p['shared_surface_area_mm2']>1 for p in row['contacts']);checks.append(row)
for h in C['partition_hole_patch']:
 kind='positive'if h['center_C_mm'][1]==-450 else'negative';n=f'MAIN_{kind}_{h["target_part"]}_gland';row=contact(n+'_LAPP53111030',n+'_LAPP53119030');row.update(kind='nominal_M25_cylindrical_thread_contact',thread_pitch_mm=1.5,engagement_mm=6,pass_=row['gap_mm']<1e-4 and row['shared_surface_area_mm2']>1);checks.append(row)
deck=cq.importers.importStep(str(P.parent/'body-power/shock-opening-study/body_deck_SO02_E04_40holes.step')).val()
feet=[]
for r in C['supports']:
 sh=new[r['id']+'_welded_stand'];bottoms=[f for f in sh.Faces()if abs(f.Center().z-103)<1e-5 and f.geomType()=='PLANE'];tops=[f for f in deck.Faces()if abs(f.Center().z-103)<1e-5 and f.geomType()=='PLANE'];area=sum(a.intersect(b).Area()for a in bottoms for b in tops)
 feet.append({'id':r['id'],'method':'Actual coplanar exported STEP face common area; solid boolean omits zero-thickness contact','area_mm2':area,'pass':abs(area-1500)<1e-3})
base=P.parent/'body-power/shock-opening-study/body_shock_partition_replacements_SO02_E04P'
b=base.with_suffix('.glb').read_bytes();jj=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);ps=list(cq.importers.importStep(str(base.with_suffix('.step'))).val());panels=dict(zip([n['name']for n in jj['nodes']],ps))
for h in C['partition_hole_patch']:
 x,y,z=h['center_C_mm'];lo,hi=h['cut_X_mm'];cut=cq.Workplane('YZ').center(y,z).circle(h['diameter_mm']/2).extrude(hi-lo).translate((lo,0,0)).val();panels[h['target_part']]=panels[h['target_part']].cut(cut)
gland_panel_checks=[]
for h in C['partition_hole_patch']:
 kind='positive'if h['center_C_mm'][1]==-450 else'negative';n=f'MAIN_{kind}_{h["target_part"]}_gland';panel=panels[h['target_part']]
 for suffix in ['_LAPP53111030','_LAPP53119030']:
  sh=new[n+suffix];area=shared_area(sh,panel);gap=sh.distance(panel);gland_panel_checks.append({'node':n+suffix,'panel':h['target_part'],'face_common_contact_area_mm2':area,'gap_mm':gap,'pass':gap<1e-5 and area>100})
bends=[{'id':r['id'],'actual_CAD_circle_R_mm':r['CAD_minimum_circular_radius_mm'],'source_nominal_limit_mm':r['source_minimum_fixed_bend_R_mm'],'pass':r['CAD_minimum_circular_radius_mm']>=r['source_minimum_fixed_bend_R_mm']-1e-5}for r in C['routes']]
out={'revision':'E05','retained_stack_contacts':checks,'full_foot_bearing_checks':feet,'exact_CAD_radius_checks':bends,'gland_panel_face_checks':gland_panel_checks,'source_geometry_SHA256':hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest(),'pass':all(r.get('pass',r.get('pass_',False))for r in checks+feet+bends+gland_panel_checks),'nominal_threads_only':True,'weld_strength_grade_torque_locking_pullout_qualified':False}
# Replace non-diagnostic solid-common areas in the previous report with actual
# face-common contact evidence. The geometry and original acceptance remain unchanged.
for r,f in zip(G['support_checks'],feet):
 r.pop('stand_deck_area_mm2',None);r['actual_coplanar_foot_contact_area_mm2']=f['area_mm2'];r['full_foot_contact_verified']=f['pass']
 for h in r['hardware']:
  if 'nominal_thread_shared_area_mm2' in h:h['solid_common_zero_thickness_area_non_diagnostic_mm2']=h.pop('nominal_thread_shared_area_mm2')
G['face_contact_supplement']='main_pair_retention_check_E05.json';G['pass']=G['pass']and out['pass']
(O/'main_pair_geometry_check_E05.json').write_text(json.dumps(G,indent=2)+'\n')
(O/'main_pair_retention_check_E05.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'feet':feet,'radii':bends}))
