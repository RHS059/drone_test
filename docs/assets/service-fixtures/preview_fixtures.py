from pathlib import Path
import struct,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
P=Path(__file__).resolve().parent

def meshes(path):
 raw=path.read_bytes();n,typ=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);pos=20+n;sz,t=struct.unpack_from('<II',raw,pos);binary=raw[pos+8:pos+8+sz]
 for node in d['nodes']:
  if 'mesh'not in node:continue
  for p in d['meshes'][node['mesh']]['primitives']:
   a=d['accessors'][p['attributes']['POSITION']];v=d['bufferViews'][a['bufferView']];arr=np.frombuffer(binary,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3)
   ma=d['materials'][p['material']]['pbrMetallicRoughness']['baseColorFactor'];yield node['name'],arr.reshape(-1,3,3),ma
fig=plt.figure(figsize=(15,7),facecolor='#f4f5f6')
for i,stem in enumerate(['chassis_trestles_S01','corner_cradle_S01']):
 ax=fig.add_subplot(1,2,i+1,projection='3d');ax.set_facecolor('#f4f5f6');allv=[]
 for name,tris,col in meshes(P/(stem+'.glb')):
  # all actual exported triangle faces, no constructed illustrative geometry
  ax.add_collection3d(Poly3DCollection(tris,facecolors=col,edgecolor=(.14,.17,.20,.22),linewidth=.06));allv.append(tris.reshape(-1,3))
 v=np.concatenate(allv);lo=v.min(0);hi=v.max(0);ax.set_xlim(lo[0]-.1,hi[0]+.1);ax.set_ylim(lo[1]-.1,hi[1]+.1);ax.set_zlim(lo[2]-.05,hi[2]+.1);ax.set_box_aspect(hi-lo);ax.view_init(elev=25,azim=-55);ax.set_xlabel('X (m)');ax.set_ylabel('Y (m)');ax.set_zlabel('Z (m)');ax.set_title('Two static chassis trestles'if i==0 else 'One wheel-corner capture cradle',pad=8)
fig.suptitle('S01 original workholding geometry • NOT LOAD-RATED • NOT LIFTING EQUIPMENT',fontsize=15)
fig.text(.02,.02,'Actual STEP-derived GLB geometry. CAD fit checks are not structural qualification.',fontsize=11,color='#7e2718');plt.tight_layout(rect=(0,.04,1,.95));fig.savefig(P/'service_fixtures_S01_preview.png',dpi=130)
