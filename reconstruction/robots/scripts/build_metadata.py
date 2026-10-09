#!/usr/bin/env python3
"""Extract the pinned source model without ROS runtime dependencies.
UR macro frame definitions are transcribed explicitly and regression checked;
Robotiq links/joints are parsed directly from the OEM macro (prefix='').
"""
import json, pathlib, math, hashlib, shutil, xml.etree.ElementTree as ET, yaml
root=pathlib.Path(__file__).resolve().parents[1]; dist=root/'dist';dist.mkdir(exist_ok=True)
UR=root/'upstream/ur';RQ=root/'upstream/robotiq'; D=RQ/'grippers/robotiq_description'
class Loader(yaml.SafeLoader):pass
Loader.add_constructor('!degrees',lambda l,n:math.radians(float(l.construct_scalar(n))))
def read(path):return yaml.load(path.read_text(),Loader=Loader)
def origin(xyz=None,rpy=None):return {'xyz':xyz or [0,0,0],'rpy':rpy or [0,0,0]}
def fromdict(d):return origin([d[k] for k in ('x','y','z')],[d[k] for k in ('roll','pitch','yaw')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(root))
def arr(s):return list(map(float,s.split()))
plan=[];used=set()
UR_COPY='© 2023 Universal Robots A/S. Use hereof is subject to Universal Robots A/S’ Terms and Conditions for Use of Graphical Documentation.'
RQ_COPY='Copyright (c) 2026, Robotiq; Copyright (c) 2022, PickNik Robotics. BSD 3-Clause.'
def asset(p,link,out,copyright):
 used.add(p);plan.append({'source':rel(p),'sha256':sha(p),'link':link,'output':out,'copyright':copyright});return out
kin=read(UR/'config/ur20/default_kinematics.yaml')['kinematics']; vis=read(UR/'config/ur20/visual_parameters.yaml')['mesh_files']; limits=read(UR/'config/ur20/joint_limits.yaml')['joint_limits']; phys=read(UR/'config/ur20/physical_parameters.yaml')['inertia_parameters']
links=[{'name':'base_link'}]
for key,name in zip(['base','shoulder','upper_arm','forearm','wrist_1','wrist_2','wrist_3'],['base_link_inertia','shoulder_link','upper_arm_link','forearm_link','wrist_1_link','wrist_2_link','wrist_3_link']):
 p=UR/vis[key]['visual']['mesh']['path'];collision=UR/vis[key]['collision']['mesh']['path'];used.add(collision)
 links.append({'name':name,'visual':{'asset':asset(p,name,f'ur20/{name}.glb',UR_COPY),'origin':fromdict(vis[key]['mesh_offset']),'scale':[1,1,1]},'source_visual':rel(p),'source_collision':rel(collision),'mass_kg':phys[key+'_mass']})
joints=[{'name':'base_link-base_link_inertia','type':'fixed','parent':'base_link','child':'base_link_inertia','origin':origin(rpy=[0,0,math.pi])}]
for i,(key,jname) in enumerate(zip(['shoulder','upper_arm','forearm','wrist_1','wrist_2','wrist_3'],['shoulder_pan_joint','shoulder_lift_joint','elbow_joint','wrist_1_joint','wrist_2_joint','wrist_3_joint'])):
 lim=limits[jname];joints.append({'name':jname,'type':'revolute','parent':links[i+1]['name'],'child':links[i+2]['name'],'origin':fromdict(kin[key]),'axis':[0,0,1],'limit':{'lower':lim['min_position'],'upper':lim['max_position'],'effort':lim['max_effort'],'velocity':lim['max_velocity']}})
for name,parent,rpy in [('ft_frame','wrist_3_link',[math.pi,0,0]),('base','base_link',[0,0,math.pi]),('flange','wrist_3_link',[0,-math.pi/2,-math.pi/2]),('tool0','flange',[math.pi/2,0,math.pi/2])]:
 links.append({'name':name});joints.append({'name':parent+'-'+name,'type':'fixed','parent':parent,'child':name,'origin':origin(rpy=rpy)})
ur={'name':'Universal Robots UR20','root':'base_link','links':links,'joints':joints,'source_mass_total_kg':sum(x.get('mass_kg',0) for x in links),'catalogue_mass_kg':64,'calibration':kin['hash'],'caveats':['Source default kinematics are not calibrated to a particular serial-number robot.','Source base mass 4.0 kg is explicitly marked possibly incorrect; total source mass is retained without normalization.','Elbow limits are planning limits of ±pi, not a claim about unrestricted mechanical joint travel.'],'physical_parameters':phys}
macro=D/'urdf/robotiq_2f_85_macro.urdf.xacro';used.add(macro)
e=ET.parse(macro).getroot();m=e.find('{http://wiki.ros.org/xacro}macro')
def clean(s):return s.replace('${prefix}','')
rl=[];rj=[]
for l in m.findall('link'):
 name=clean(l.attrib['name']);p=D/l.find('visual/geometry/mesh').attrib['filename'].split('package://robotiq_description/')[1]; cp=D/l.find('collision/geometry/mesh').attrib['filename'].split('package://robotiq_description/')[1];used.add(cp)
 inertia=l.find('inertial'); ip=inertia.find('origin');it=inertia.find('inertia')
 rl.append({'name':name,'visual':{'asset':asset(p,name,f'robotiq/{name}.glb',RQ_COPY),'origin':origin(),'scale':[1,1,1]},'source_visual':rel(p),'source_collision':rel(cp),'mass_kg':float(inertia.find('mass').attrib['value']),'inertial':{'origin':origin(arr(ip.attrib['xyz']),arr(ip.attrib['rpy'])),'inertia':{k:float(v) for k,v in it.attrib.items()}}})
for j in m.findall('joint'):
 if j.find('parent').attrib['link']=='${parent}':continue
 o=j.find('origin');a=j.find('axis');lim=j.find('limit');mi=j.find('mimic')
 x={'name':clean(j.attrib['name']),'type':j.attrib['type'],'parent':clean(j.find('parent').attrib['link']),'child':clean(j.find('child').attrib['link']),'origin':origin(arr(o.attrib.get('xyz','0 0 0')),arr(o.attrib.get('rpy','0 0 0')))}
 if a is not None:x['axis']=arr(a.attrib['xyz'])
 if lim is not None:x['limit']={k:float(v) for k,v in lim.attrib.items()}
 if mi is not None:x['mimic']={'joint':clean(mi.attrib['joint']),'multiplier':float(mi.attrib.get('multiplier',1)),'offset':float(mi.attrib.get('offset',0))}
 rj.append(x)
rq={'name':'Robotiq 2F-85','root':'robotiq_85_base_link','links':rl,'joints':rj,'driver_joint':'robotiq_85_left_knuckle_joint','command_range_rad':[0,0.8],'closed_control_default_rad':0.7929,'source_mass_total_kg':sum(x['mass_kg'] for x in rl)}
cp=D/'meshes/visual/2f_85/ur_to_robotiq_adapter.dae'
used.add(D/'urdf/ur_to_robotiq_adapter.urdf.xacro');used.add(D/'meshes/collision/2f_85/ur_to_robotiq_adapter.stl')
# OEM 2F85 coupling macro directly specifies zero visual origin and +11mm
# gripper_side_joint. No private STEP or geometry correction is used.
cpasset=asset(cp,'robotiq_coupling','robotiq/robotiq_coupling.glb',RQ_COPY)
meta={'schema_version':1,'reconstruction_status':'new reconstruction from pinned public source; previous audited archive unavailable','units':{'length':'metre','angle':'radian','mass':'kg'},'coordinate_system':'right-handed native ROS Z-up; GLB preserves source axes; do not rotate loader roots','transform_order':'T_world_child = T_world_parent * T_xyz * Rz(yaw) * Ry(pitch) * Rx(roll) * R_axis(q); visual origin applied after link transform','ur20':ur,'robotiq':rq,'mount_chain':[{'name':'tool0_to_adapter','parent':'tool0','child':'adapter','origin':origin(rpy=[0,0,math.pi])},{'name':'adapter_to_coupling','parent':'adapter','child':'robotiq_coupling','origin':origin([0,0,0.0235])},{'name':'coupling_to_gripper','parent':'robotiq_coupling','child':rq['root'],'origin':origin([0,0,0.011])}],'coupling':{'name':'robotiq_coupling','visual':{'asset':cpasset,'origin':origin(),'scale':[1,1,1]},'source':rel(cp),'caveat':'Licensed OEM 2F85 ur_to_robotiq_adapter.dae; zero visual origin and +11mm gripper seating explicitly from source ur_to_robotiq_adapter.urdf.xacro. Not private STEP or manufacturing drawing. −3mm outer skirt must clear project adapter; physical fit not certified.'},'notices':{'ur20':UR_COPY,'robotiq':RQ_COPY}}
(dist/'robot-kinematics.json').write_text(json.dumps(meta,indent=2)+'\n');(root/'conversion-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
# Complete original source subset and notices are distributable with the viewer.
for p in [UR/'LICENSE',UR/'meshes/ur20/LICENSE.txt',RQ/'LICENSE',RQ/'grippers/LICENSE',UR/'urdf/ur_macro.xacro',UR/'urdf/inc/ur_common.xacro',D/'package.xml',UR/'package.xml',*list((UR/'config/ur20').glob('*.yaml')),UR/'meshes/ur20/visual/UR20_DIFF_8bit_2K.png']:
 used.add(p)
licenses=dist/'licenses';licenses.mkdir(exist_ok=True)
for p,name in [(UR/'LICENSE','UR-ROS-DESCRIPTION-LICENSE'),(UR/'meshes/ur20/LICENSE.txt','UR-GRAPHICAL-TERMS.txt'),(RQ/'LICENSE','ROBOTIQ-LICENSE'),(RQ/'grippers/LICENSE','ROBOTIQ-GRIPPERS-LICENSE')]:shutil.copy2(p,licenses/name)
manifest={'sources':[{'repository':'https://github.com/UniversalRobots/Universal_Robots_ROS2_Description','commit':'6662e15f32c23c12ece57d0050aee9a716e4fc41'},{'repository':'https://github.com/Robotiq/ros','commit':'adb20dc0048ff2ef51c5a86fe2f7880a8618f099'}],'files':[]}
for p in sorted(used):
 destination=dist/'source'/p.relative_to(root/'upstream'); destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,destination)
 manifest['files'].append({'path':str(destination.relative_to(dist)),'sha256':sha(p),'bytes':p.stat().st_size})
(dist/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Metadata:',len(ur['links']),len(ur['joints']),'UR links/joints;',len(rl),len(rj),'Robotiq links/joints;',len(plan),'mesh conversions')
