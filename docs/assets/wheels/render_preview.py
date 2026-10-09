"""Non-Blender analytic mesh preview and original-section plot for visual QA."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/matplotlib-wheel')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from verify_wheel import glb_read
from build_wheel import tire_profile
P=Path(__file__).resolve().parent
j,acc=glb_read(P/'wheel_C01.glb')
fig=plt.figure(figsize=(11,9),facecolor='#e8edf1');ax=fig.add_subplot(111,projection='3d');ax.set_facecolor('#e8edf1')
light=np.array([.6,1.,1.3]);light/=np.linalg.norm(light)
for mesh in j['meshes']:
 pr=mesh['primitives'][0];v=acc(pr['attributes']['POSITION']);f=acc(pr['indices']).flatten().reshape(-1,3);tri=v[f]
 no=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-20)
 shade=.40+.60*np.maximum(0,no@light)
 base=np.array([.21,.24,.25]) if mesh['name']=='tire' else np.array([.69,.75,.77])
 colors=np.clip(base[None,:]*shade[:,None],0,1)
 ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors='none',linewidths=0,rasterized=True))
ax.set_xlim(-.46,.46);ax.set_ylim(-.46,.46);ax.set_zlim(-.46,.46);ax.set_box_aspect([1,1,1]);ax.view_init(elev=22,azim=58);ax.set_axis_off()
fig.suptitle('Original source-backed wheel C01',fontsize=17,y=.94)
fig.text(.5,.10,'876.3 mm provisional OD  |  317.5 mm section envelope  |  18 x 8.5 in bead interface',ha='center',fontsize=10)
fig.text(.5,.07,'Generic original tread and perforated disc. Not OEM CAD or manufacturing approval.',ha='center',fontsize=10)
fig.savefig(P/'wheel_C01_preview.png',dpi=150,bbox_inches='tight');plt.close(fig)
p=np.array(tire_profile());fig,ax=plt.subplots(figsize=(9,6));ax.fill(p[:,1],p[:,0],color='#26353b',alpha=.8);ax.plot(p[:,1],p[:,0],color='black',lw=.7)
ax.set_aspect('equal');ax.set_xlabel('Axial Y (mm)');ax.set_ylabel('Radius from axle (mm)');ax.grid(alpha=.3)
ax.set_title('Original annular tire section C01\nOutside dimensions provisional on selected 8.5 in rim')
ax.text(0,260,'Open air cavity\nOriginal assumed inner profile',ha='center',fontsize=10)
fig.savefig(P/'tire_C01_section.png',dpi=140,bbox_inches='tight')
