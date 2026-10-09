from pathlib import Path
import sys,json,hashlib,cadquery as cq
P=Path(__file__).resolve().parent;O=P/'main_routes_E05';sys.path.insert(0,str(P.parent/'body-power/shock-opening-study'));import build_shock_openings_SO01 as mech
C=json.loads((O/'main_pair_contract_E05.json').read_text());new=list(cq.importers.importStep(str(O/'main_pair_supported_E05.step')).val());D=dict(zip([p['name']for p in C['parts']],new));assert len(D)==len(new)
bad=[];pairs=0;exact=0;mins=[]
new_bounds={n:mech.bb(s)for n,s in D.items()}
new_solids={n:[(sa,mech.bb(sa))for sa in s.Solids()]for n,s in D.items()}
for c in mech.corners():
 print('CORNER',c['name'],flush=True)
 for q in range(-12,13,2):
  obstacles=[(n,s,mech.bb(s))for n,s in [('tower',c['shape'])]+mech.modules(c,q)]
  for n,s in D.items():
   a=new_bounds[n]
   for m,t,b in obstacles:
    pairs+=1
    if not mech.near(a,b):continue
    exact+=1;v=0.
    for sa,sa_bb in new_solids[n]:
     if mech.near(sa_bb,b):
      print('EXACT_PAIR',n,c['name'],q,m,flush=True);v+=sa.intersect(t).Volume()
    if v>1e-3:bad.append({'part':n,'corner':c['name'],'q_deg':q,'obstacle':m,'volume_mm3':v})
report={'source_geometry_SHA256':hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest(),'revision':'E05_candidate','sampled_corner_poses':78,'pairs':pairs,'exact_AABB_candidates':exact,'overlaps':bad,'pass':not bad,'continuous_motion_or_flexible_cable_dynamics_qualified':False}
(O/'main_pair_mechanical_check_E05.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
