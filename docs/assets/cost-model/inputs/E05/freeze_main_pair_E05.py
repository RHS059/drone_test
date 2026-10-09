"""Freeze the bounded two-route module only after exact checks pass."""
from pathlib import Path
import cadquery as cq,json,hashlib,zipfile,struct
import cad_export_E05 as ce
P=Path(__file__).resolve().parent;O=P/'main_routes_E05';ce.P=O
C=json.loads((O/'main_pair_contract_E05.json').read_text());G=json.loads((O/'main_pair_geometry_check_E05.json').read_text());M=json.loads((O/'main_pair_mechanical_check_E05.json').read_text());assert G['pass']and M['pass'],'Do not freeze rejected or pending routes'
V=json.loads((O/'visual_endplane_check_E05.json').read_text());assert V['pass']and V['GLB_SHA256']==hashlib.sha256((O/'main_pair_supported_E05.glb').read_bytes()).hexdigest()
R=json.loads((O/'main_pair_retention_check_E05.json').read_text());assert R['pass'],'Retention/contact checks must pass'
assert R['source_geometry_SHA256']==hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest()
assert G['source_hashes']['electrical-drive/main_routes_E05/main_pair_supported_E05.step']==hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest()
assert M['source_geometry_SHA256']==hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest(),'Wrong mechanical geometry revision'
base=P.parent/'body-power/shock-opening-study/body_shock_partition_replacements_SO02_E04P';b=base.with_suffix('.glb').read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);ss=list(cq.importers.importStep(str(base.with_suffix('.step'))).val());body=dict(zip([n['name']for n in j['nodes']],ss));names=['controller_battery_partition','battery_tool_partition'];before={n:body[n].Volume()for n in names}
for h in C['partition_hole_patch']:
 x,y,z=h['center_C_mm'];lo,hi=h['cut_X_mm'];cut=cq.Workplane('YZ').center(y,z).circle(h['diameter_mm']/2).extrude(hi-lo).translate((lo,0,0)).val();body[h['target_part']]=body[h['target_part']].cut(cut)
parts=[(n,body[n],'steel','Original body partition named replacement: two source-sizedM25 throughbores. Preserve all other E04Pgeometry; original aluminium body, colour does not imply steel material.')for n in names]
ce.CUSTOM_TESS={};meta=ce.export('partition_main_glands_E05',parts,{'source':'Original SO02_E04P body partition delta, four source-sized LAPP gland mounting bores','vehicle_placed':True})
patch={'revision':'E05','source_body_package':str(base.relative_to(P.parent)),'source_body_STEP_SHA256':hashlib.sha256(base.with_suffix('.step').read_bytes()).hexdigest(),'replace_by_name':names,'cutters':C['partition_hole_patch'],'volume_checks':[{'name':n,'before_mm3':before[n],'after_mm3':body[n].Volume(),'removed_mm3':before[n]-body[n].Volume()}for n in names],'geometry':meta,'deck_40_bores_unchanged':True,'body_strength_weather_and_installed_IP_qualified':False};(O/'partition_patch_E05.json').write_text(json.dumps(patch,indent=2)+'\n')
for r in C['parts']:
 r['actual_material']=('aluminium matched to selected deck; exact alloy/temper pending'if r['name'].endswith('_welded_stand')else 'original clamp polymer/liner unspecified'if r['name'].endswith(('_lower_clamp','_upper_clamp'))else 'source cable insulation envelope'if r['name'].endswith('_routed_jacket')else 'purchased gland/locknut representation'if '_LAPP' in r['name']else 'nominal steel hardware; grade and locking unspecified')
 r['display_palette_is_not_material_specification']=True
nodes={r['name']:{'module':'main_pair_E05','source_node':r['name'],'actual_material':r['actual_material']}for r in C['parts']};edges=[]
def edge(kind,a,b,ret=[],evidence=[],gates=[],**kw):edges.append({'id':f'E05_{len(edges):03}','kind':kind,'from_nodes':a,'to_nodes':b,'retaining_nodes':ret,'evidence':evidence,'open_gates':gates,**kw})
for r in C['routes']:
 n=r['id']+'_70mm2_routed_jacket'
 edge('source_anchored_continuous_DC_cable_jacket',[n],[r['from'],r['to']],evidence=['main_pair_geometry_check_E05.json'],gates=['Lug crimp/conductor contact and exact strip/tool process unqualified','Cable thermal rating, voltage drop, environment and positive marking unqualified','Upstream fuse/merge hardware remains missing; system must not be energized'],jacket_endface_coordinates_verified=True,conductive_contact_and_operational_circuit_verified=False,domain='DC_power')
for r in C['supports']:
 n=r['id'];cable='_'.join(n.split('_')[:2])+'_70mm2_routed_jacket';hw=[n+f'_{p}_{i}'for i in [0,1]for p in ['M4x30','upper_washer','lower_washer','M4nut']]
 edge('split_clamp_retains_jacket',[n+'_lower_clamp',n+'_upper_clamp'],[cable,n+'_welded_stand'],hw,['main_pair_geometry_check_E05.json'],['Clamp polymer/liner, torque, pullout, abrasion and vibration qualification open','M4nominal cylindrical threads, nohelix/grade/locking claim'],nominal_geometric_contact_verified=True)
 edge('proposed_matched_aluminium_weld_contact',[n+'_welded_stand'],['body/main_base_deck_3mm'],evidence=['main_pair_geometry_check_E05.json','main_pair_retention_check_E05.json'],gates=['Deck aluminium has only a 5083-like density assumption. Exact matching alloy/temper, weld filler/process/size, heat-affected-zone effects, thin-deck fatigue and stand strength are unqualified'],foot_plane_Z_mm=103,foot_contact_mm2=1500,nominal_geometric_contact_verified=True,welded_load_path_qualified=False,stand_and_deck_intended_material_family='aluminium matched pair')
for h in C['partition_hole_patch']:
 kind='positive'if h['center_C_mm'][1]==-450 else'negative';n=f'MAIN_{kind}_{h["target_part"]}_gland';edge('retained_source_M25_gland',[n+'_LAPP53111030'],['body/'+h['target_part'],'MAIN_'+kind+'_70mm2_routed_jacket'],[n+'_LAPP53119030'],['main_pair_geometry_check_E05.json','partition_patch_E05.json'],['Installed sealing/IP, cable clamp pullout, tightening torque and thermal environment not released'],source_thread_engagement_mm=6,thread_protrusion_mm=1,nominal_geometric_contact_verified=True)
covered=set()
for e in edges:covered.update(e['from_nodes']+e['to_nodes']+e['retaining_nodes'])
assert set(nodes)<=covered,set(nodes)-covered
C['remaining_upstream_gates']=['Covered <=100 A pack fuses with source mount/terminal datums','Source-rated retained positive and negative merge','Main positive fuse and coordination','Battery terminal source revision confirmation; polarity verified separately by R01']
C['cable_source_and_scenario']='cable_source_and_scenario_E05.json'
C['source_urls'].append(json.loads((O/'cable_source_and_scenario_E05.json').read_text())['official_source'])
C['source_material_record']='body-power/verification.json: aluminium, 5083-like density only; exact alloy/temper and weld process unqualified'
C.update(revision='E05_frozen_two_route_candidate',required_geometry_checks_passed=True,freeze=True,source_E04_unchanged=True,geometry_file_SHA256={f:hashlib.sha256((O/f).read_bytes()).hexdigest()for f in ['main_pair_supported_E05.step','main_pair_supported_E05.glb']},body_partition_delta='partition_patch_E05.json',connection_graph='main_pair_graph_E05.json',selected_route_scope='Only Q0:P_OUT→LYNX:BAT+ and Q0:N_OUT→LYNX:BAT−. Upstream battery/merge/protection and all other branches remain open. No motorport changes.')
(O/'main_pair_contract_E05.json').write_text(json.dumps(C,indent=2)+'\n');(O/'main_pair_graph_E05.json').write_text(json.dumps({'revision':'E05','nodes':nodes,'edges':edges,'all98_rendered_nodes_accounted':True,'complete_upstream_or_operating_electrical_system':False},indent=2)+'\n')
files=['build_main_pair_E05.py','cad_export_E05.py','check_main_pair_E05.py','check_main_pair_mechanical_E05.py','freeze_main_pair_E05.py','check_main_pair_retention_E05.py','align_main_pair_visual_E05.py']+['main_routes_E05/'+f for f in ['main_pair_supported_E05.step','main_pair_supported_E05.glb','main_pair_contract_E05.json','main_pair_geometry_check_E05.json','main_pair_mechanical_check_E05.json','partition_main_glands_E05.step','partition_main_glands_E05.glb','partition_patch_E05.json','main_pair_graph_E05.json','battery_polarity_regression_E05.py','battery_polarity_regression_E05.json','cable_separation_screen_E05.json','main_pair_retention_check_E05.json','cable_source_and_scenario_E05.json','README_E05.md','INPUT_HASHES_E05.json','bom_E05.json','visual_endplane_check_E05.json']]
manifest={'revision':'E05','allowlist':files,'sha256':{f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in files},'reject':['rejected_R00','logs','review screenshots','all supplier CAD/PDF/images'],'runtime_assets':['main_routes_E05/main_pair_supported_E05.glb','main_routes_E05/partition_main_glands_E05.glb'],'replace_E04_body_names':names,'remove_optional_E04_lead_nodes':C['existing_E04_overlays_to_remove'],'geometry_and_endpoint_route_candidate_only':True,'electrically_operational':False}
(O/'PUBLIC_FILES_E05.json').write_text(json.dumps(manifest,indent=2)+'\n')
zp=P/'original_main_pair_E05.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,9)as z:
 for f in files+['main_routes_E05/PUBLIC_FILES_E05.json']:z.write(P/f,f)
d={'revision':'E05','zip_file':zp.name,'zip_sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'bytes':zp.stat().st_size,'manifest_SHA256':hashlib.sha256((O/'PUBLIC_FILES_E05.json').read_bytes()).hexdigest(),'contract_SHA256':hashlib.sha256((O/'main_pair_contract_E05.json').read_bytes()).hexdigest(),'system_complete':False};(O/'FREEZE_E05.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
