import build_body_power as b
import json,hashlib
b.build();b.finish_seams()
r=json.loads((b.P/'verification.json').read_text())
assert len(b.PARTS)==r['original_part_count']
# Geometry unchanged since full verification; only presentation colors updated.
for p in b.PARTS:
 old=next(x for x in r['parts'] if x['name']==p['name'])
 assert abs(p['shape'].Volume()*1e-9-old['volume_m3'])<1e-12,p['name']
for pp,stem in [(b.PARTS,'body_power_R01'),(b.PROXIES,'cots_reservations_R01')]:
 ass=b.cq.Assembly(name=stem)
 for p in pp:ass.add(p['shape'],name=p['name'],color=b.cq.Color(*b.MATS[p['material']]['color']))
 ass.export(str(b.P/(stem+'.step')));b.export_glb(pp,b.P/(stem+'.glb'))
r['material_assumptions']=b.MATS;r['visual_finish']='Warm gray/sand visualization only; no coating specification or supplier finish selection.'
(b.P/'verification.json').write_text(json.dumps(r,indent=2))
# Orthographic-style engineering geometry QA figure, using exact CAD tessellation rather than generated imagery.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
for cut in [False,True]:
 fig=plt.figure(figsize=(18,9),dpi=120);ax=fig.add_subplot(111,projection='3d');tris=[];colors=[]
 for p in b.PARTS:
  if cut and (p['group'] in ['hatches','battery_hatch','tool_hatch'] or p['name'].endswith('sloping_shoulder') or p['name'] in ['main_left_side_3mm','front_tool_hatch_removable_lid']):continue
  vs,ts=p['shape'].tessellate(.9,.25);v=np.array([[x.x,x.y,x.z] for x in vs])/1000;tri=v[np.array(ts)];tris.extend(tri);color=b.MATS[p['material']]['color'];colors.extend([color]*len(tri))
 if cut:
  for p in b.PROXIES:
   vs,ts=p['shape'].tessellate(.9,.25);v=np.array([[x.x,x.y,x.z] for x in vs])/1000;tri=v[np.array(ts)];tris.extend(tri);colors.extend([[.77,.43,.13,.5]]*len(tri))
 poly=Poly3DCollection(tris,facecolors=colors,edgecolors='none',linewidths=0);ax.add_collection3d(poly)
 ax.set_xlim(-2.1,2.1);ax.set_ylim(-.72,.72);ax.set_zlim(-.16,.4);ax.set_box_aspect([4.2,1.44,.56]);ax.view_init(elev=29,azim=-58);ax.set_xlabel('X forward (m)');ax.set_ylabel('Y left (m)');ax.set_zlabel('Z up (m)');ax.set_title('Original body/power R01 — '+('service cutaway; orange cuboids are DIMENSION ONLY' if cut else 'manufacturing-development CAD; warm finish is illustrative'))
 fig.tight_layout();fig.savefig(b.P/('body_cutaway_qa.png' if cut else 'body_closed_qa.png'));plt.close(fig)
print('Final colors, hashes and two engineering CAD QA images exported.')
