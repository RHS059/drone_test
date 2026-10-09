from pathlib import Path
import cadquery as cq,json,struct,hashlib,numpy as np
P=Path(__file__).resolve().parent;O=P/'main_routes_E05';B=P.parent/'body-power';E=P
C=json.loads((O/'main_pair_contract_E05.json').read_text())
def load(p):
 p=Path(p);b=p.with_suffix('.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);ss=list(cq.importers.importStep(str(p.with_suffix('.step'))).val());assert len(ss)==len(j['nodes']),(p,len(ss),len(j['nodes']));return dict(zip([n['name']for n in j['nodes']],ss))
body=load(B/'panel-retention/body_power_panel_retained_PR01');body.update(load(B/'shock-opening-study/body_shock_partition_replacements_SO02_E04P'))
t=json.loads((E/'victron_candidate/switchgear_E04/rear_trough_patch_contract.json').read_text())
for r in t['changes']:
 if r['action']in ['remove','replace']:body.pop(r['name'])
body.update(load(E/'victron_candidate/switchgear_E04/aligned_trough_and_glands_E04'))
patch=[]
for h in C['partition_hole_patch']:
 x,y,z=h['center_C_mm'];lo,hi=h['cut_X_mm'];cut=cq.Workplane('YZ').center(y,z).circle(h['diameter_mm']/2).extrude(hi-lo).translate((lo,0,0)).val();old=body[h['target_part']];new=old.cut(cut);v=old.Volume()-new.Volume();patch.append({'target':h['target_part'],'axis_C_mm':h['center_C_mm'],'removed_volume_mm3':v,'full3mm_cylinder_mm3':np.pi*(h['diameter_mm']/2)**2*3,'full_panel_bore':abs(v-np.pi*(h['diameter_mm']/2)**2*3)<1e-4});body[h['target_part']]=new
hardware=load(E/'carrier_freeze_E02/original_electrical_carriers_E02');LC=json.loads((E/'victron_candidate/lynx_E04/lynx_mounted_contract.json').read_text())
for n in LC['patch']['remove']+LC['patch']['replace']:hardware.pop(n)
for p in ['victron_candidate/controllers_E04/controller_housing_interfaces_E04','victron_candidate/controllers_E04/UR_OEMDC_cases_UNRETAINED_E04','victron_candidate/lynx_E04/lynx1000_mounted_E04','victron_candidate/switchgear_E04/installed_isolators_E04']:hardware.update(load(E/p))
new=load(O/'main_pair_supported_E05')
BBOX_CACHE={}
SOLID_CACHE={}
def solids(s):
 k=id(s)
 if k not in SOLID_CACHE:SOLID_CACHE[k]=(s,s.Solids())
 return SOLID_CACHE[k][1]
def bb(s):
 k=id(s)
 if k not in BBOX_CACHE:
  b=s.BoundingBox();BBOX_CACHE[k]=(s,[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
 return BBOX_CACHE[k][1]
def check(a,b):
 bad=[];contact=[]
 for an,sh in a.items():
  print('TEST_PART',an,flush=True)
  aa=bb(sh)
  for bn,t in b.items():
   if an==bn or a is b and an>bn:continue
   bbb=bb(t)
   if any(aa[k]>bbb[k+3]+1e-4 or bbb[k]>aa[k+3]+1e-4 for k in range(3)):continue
   # Body intersection acts on compound cable segments, each exact swept circular section.
   v=0.
   for sa in solids(sh):
    aa1=bb(sa)
    for sb in solids(t):
     bb1=bb(sb)
     if all(aa1[k]<=bb1[k+3]+1e-5 and bb1[k]<=aa1[k+3]+1e-5 for k in range(3)):
      print('EXACT_PAIR',an,bn,flush=True);v+=sa.intersect(sb).Volume()
   if v>1e-3:bad.append({'a':an,'b':bn,'volume_mm3':v})
   elif not an.endswith('routed_jacket') and not bn.endswith('routed_jacket') and sh.distance(t)<1e-4:contact.append({'a':an,'b':bn})
 return bad,contact
print('CHECK_ASSEMBLY',flush=True);bad,contacts=check(new,{**body,**hardware});print('ASSEMBLY_DONE',json.dumps(bad),flush=True);own,oc=check(new,new);print('SELF_DONE',json.dumps(own),flush=True)
sc=[]
for r in C['supports']:
 n=r['id'];stand=new[n+'_welded_stand'];deck=body['main_base_deck_3mm'];lower=new[n+'_lower_clamp'];upper=new[n+'_upper_clamp'];cable=new['_'.join(n.split('_')[:2])+'_70mm2_routed_jacket'];row={'id':n,'stand_deck_gap_mm':stand.distance(deck),'solid_common_zero_thickness_area_non_diagnostic_mm2':stand.intersect(deck).Area(),'lower_stand_gap_mm':lower.distance(stand),'halves_gap_mm':upper.distance(lower),'clamp_cable_gap_mm':min(lower.distance(cable),upper.distance(cable)),'hardware':[]}
 for i in [0,1]:
  bolt=new[n+f'_M4x30_{i}'];nut=new[n+f'_M4nut_{i}'];row['hardware'].append({'bolt_nut_gap_mm':bolt.distance(nut),'solid_common_zero_thickness_area_non_diagnostic_mm2':bolt.intersect(nut).Area()})
 row['pass']=max(row[k]for k in ['stand_deck_gap_mm','lower_stand_gap_mm','halves_gap_mm','clamp_cable_gap_mm'])<1e-4 and all(h['bolt_nut_gap_mm']<1e-4 for h in row['hardware']);sc.append(row)
# The9segments per cable must meet exactly; this is a computational seam, not an open cable end.
segments=[]
for r in C['routes']:
 ss=new[r['id']+'_70mm2_routed_jacket'].Solids();gaps=[ss[i].distance(ss[i+1])for i in range(len(ss)-1)];segments.append({'id':r['id'],'seam_gaps_mm':gaps,'all_seams_closed':max(gaps)<1e-4,'sampled_bend_limit_pass':r['sampled_min_radius_mm']>=r['source_minimum_fixed_bend_R_mm']-1e-3})
endpoint_checks=[]
for r in C['routes']:
 cable=new[r['id']+'_70mm2_routed_jacket'];faces=[f for f in cable.Faces()if f.geomType()=='PLANE']
 for end,p in [('start',r['start_C_mm']),('end',r['end_C_mm'])]:
  distances=[(f.Center().sub(cq.Vector(*p)).Length,f.Area())for f in faces];d,area=min(distances);endpoint_checks.append({'route':r['id'],'end':end,'source_lug_mouth_C_mm':p,'actual_endface_center_error_mm':d,'actual_endface_area_mm2':area,'circle_area_mm2':np.pi*7.1**2,'source_anchor_meets_jacket_endface':d<1e-4 and abs(area-np.pi*7.1**2)<1e-3,'internal_crimp_contact_qualified':False})
out={'endpoint_checks':endpoint_checks,'revision':'E05_candidate','scope':'Actual composed PR01+SO02_E04P+E04trough, all retained E02+E04 electronics, new E05 cable/support/gland solids. Upstream incomplete; source cable ampacity/crimps/IP/weld qualification open.','body_patch_simulated_not_applied':True,'panel_cut_checks':patch,'assembly_overlaps':bad,'self_overlaps':own,'contacts':contacts+oc,'support_checks':sc,'continuous_segment_checks':segments,'pass':all(r['source_anchor_meets_jacket_endface']for r in endpoint_checks)and not bad and not own and all(r['pass']for r in sc)and all(r['full_panel_bore']for r in patch)and all(r['all_seams_closed']and r['sampled_bend_limit_pass']for r in segments),'electrically_operational':False,'source_hashes':{str(p.relative_to(P.parent)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [O/'main_pair_supported_E05.step',B/'shock-opening-study/body_shock_partition_replacements_SO02_E04P.step']}}
(O/'main_pair_geometry_check_E05.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['pass','assembly_overlaps','self_overlaps']}))
