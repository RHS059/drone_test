"""Independent file-level geometric screens, no load/operation qualification."""
from pathlib import Path
import cadquery as cq
import json,sys,math
from build_fixtures import bounds,overlaps,cyl,PARAM
P=Path(__file__).resolve().parent
MECH=P.parent/'mechanical'
BASE=P.parent
report={'revision':'S01','fabrication_release':False,'rated_load_kg':None,'test_scope':'Nominal exported B-rep geometry only, not strength, stability, tolerances, floor capacity or an approved lifting/removal sequence.'}
def load(path):return cq.importers.importStep(str(path)).val()
def pair(a,b):
 if not overlaps(bounds(a),bounds(b)):return None
 v=a.intersect(b).Volume()
 return {'intersection_mm3':v,'minimum_distance_mm':a.distance(b)}
def screen(a,b,label):
 clashes=[];touch=[];am=a.Solids();bm=b.Solids();ab=[bounds(s)for s in am];bb=[bounds(s)for s in bm]
 for i,aa in enumerate(am):
  for j,ss in enumerate(bm):
   if not overlaps(ab[i],bb[j]):continue
   v=aa.intersect(ss).Volume()
   if v>1e-3:clashes.append([i,j,v])
   elif aa.distance(ss)<1e-5:touch.append([i,j])
 print(label,'clashes',len(clashes),'contacts',len(touch),flush=True)
 return {'positive_volume_intersections_mm3':clashes,'zero_gap_solid_contacts':touch}
frame=load(MECH/'frame_R07.step');body=load(BASE/'body-power'/'body_power_R01.step')
t=load(P/'chassis_trestles_S01.step');c=load(P/'corner_cradle_S01.step')
report['chassis_trestles_vs_frame_R07']=screen(t,frame,'frame')
report['chassis_trestles_vs_body_R01']=screen(t,body,'body')
# Wheel geometric screen across all six corners; tires/rims are ORIGINAL source-backed C01.
wheel=load(BASE/'wheels'/'wheel_C01.step')
cl=[]
for x in [-1350,0,1350]:
 for sign in [-1,1]:
  w=wheel if sign==1 else wheel.rotate((0,0,0),(0,0,1),180)
  w=w.translate((x,sign*940,-250))
  cl.append({'station_X_mm':x,'side':sign,**screen(t,w,f'tire {x} {sign}')})
report['trestles_vs_all_six_original_wheels']=cl
w=wheel.translate((0,940,-250))
report['cradle_vs_original_wheel']=screen(c,w,'cradle wheel')
report['cradle_vs_body']=screen(c,body,'cradle body')
report['cradle_at_all_stations_vs_trestles_and_body']=[]
for xx in [-1350,0,1350]:
 for sg in [-1,1]:
  cc=c if sg==1 else c.rotate((0,0,0),(0,0,1),180)
  cc=cc.translate((xx,0,0))
  report['cradle_at_all_stations_vs_trestles_and_body'].append({'station_X_mm':xx,'side':sg,'trestles':screen(cc,t,f'cradle-trestles {xx} {sg}'),'body':screen(cc,body,f'cradle-body {xx} {sg}')})
# Actual original C02 links and carriers, no commercial drive STEP is read.
gear=BASE/'corners';parts={}
for nm in ['stationary_clamp_C02_R01','inner_backing_C02_R01','upper_wishbone_C02_R02','lower_wishbone_C02_R02','upright_pins_C02_R02']:
 parts[nm]=load(gear/(nm+'.step'))
u=load(gear/'upright_WD220_C02_R04.step').rotate((0,0,0),(1,0,0),90).translate((0,797,-250))
parts['original_upright_C02_R04']=u
a=load(gear/'wheel_adapter_C02_R02.step').rotate((0,0,0),(1,0,0),-90).translate((0,928,-250))
parts['original_wheel_adapter_C02_R02']=a
report['cradle_vs_C02_original_corner']={n:screen(c,s,n)for n,s in parts.items()}
# Extraction is symmetric ±X up to 180 mm beyond nominal pin envelope.
report['pin_extraction_screens']=[]
for z in [-80,-420]:
 e=cyl(14,520,(-260,812,z),(1,0,0))
 report['pin_extraction_screens'].append({'axis':'X','pin_Z_mm':z,'envelope_radius_mm':14,'X_span_mm':[-260,260],**screen(c,e,f'pin {z}')})
report['important_not_tested']=['Proprietary drive geometry is not read or redistributed; its envelope/mass/CG and lifting method are unqualified.','Wishbone support fixtures and coilover energy control are absent: no permission to withdraw the pins.','All suspension sweep and lowered/raised load-transfer states: only C02 q=0 static fit screened.','Human/tool clearance beyond the stated pin extraction cylinder.','Cradle insertion beneath vehicle, actual jack/hoist lift points and equipment path.','Body-frame service connectors/brake isolation.','Whole-vehicle CG, support reactions and floor loading.']
# File roundtrip checks, including named GLB node count matching STEP solid count.
report['export_roundtrip']=[]
import struct,numpy as np
for stem,obj in [('chassis_trestles_S01',t),('corner_cradle_S01',c)]:
 d=(P/(stem+'.glb')).read_bytes();length,tag=struct.unpack_from('<II',d,12);doc=json.loads(d[20:20+length]);mins=[];maxs=[]
 for mesh in doc['meshes']:
  for prim in mesh['primitives']:
   ac=doc['accessors'][prim['attributes']['POSITION']];mins.append(ac['min']);maxs.append(ac['max'])
 gb=list(np.min(mins,axis=0)*1000)+list(np.max(maxs,axis=0)*1000)
 sb=bounds(obj)
 report['export_roundtrip'].append({'file':stem,'STEP_solid_count':len(obj.Solids()),'GLB_nodes':len(doc['nodes']),'STEP_valid':obj.isValid(),'bounds_max_delta_mm':float(np.max(np.abs(np.array(gb)-sb))),'STEP_bounds_mm':sb,'GLB_bounds_mm':gb})
(P/'interface_verification_S01.json').write_text(json.dumps(report,indent=2))
print('VERIFICATION COMPLETE',flush=True)
