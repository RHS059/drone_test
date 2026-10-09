#!/usr/bin/env python3
"""Deterministic OEM COLLADA/STL to GLB conversion, using installed NumPy.
Preserves triangles, normals, colors, UVs, scene-node transforms and original PNG
bytes. No decimation or invented geometry. Native ROS Z-up, metres retained.
GLTF base-color uses original diffuse material color/texture; Phong shininess
is mapped to PBR roughness. Source XML is retained for exact material provenance.
"""
import json,pathlib,hashlib,struct,xml.etree.ElementTree as ET, numpy as np
root=pathlib.Path(__file__).resolve().parents[1]
NS={'c':'http://www.collada.org/2005/11/COLLADASchema'}
def sub(e,path):return e.find(path,NS)
def many(e,path):return e.findall(path,NS)
def numbers(s):return np.fromstring(s,sep=' ')
def ident():return np.eye(4)
class GLB:
 def __init__(self,item):
  self.data=bytearray(); self.g={'asset':{'version':'2.0','generator':'Six-Wheel Builder OEM DAE/STL converter 1.0','copyright':item['copyright'],'extras':{'axes':'native ROS Z_UP','source':item['source'],'source_sha256':item['sha256']}},'buffers':[{}],'bufferViews':[],'accessors':[],'meshes':[],'nodes':[],'materials':[],'scenes':[{'nodes':[]}],'scene':0};self.bounds=[];self.triangles=0
 def blob(self,data,target=None):
  self.data+=b'\0'*((-len(self.data))%4); i=len(self.g['bufferViews']);o={'buffer':0,'byteOffset':len(self.data),'byteLength':len(data)}
  if target:o['target']=target
  self.g['bufferViews'].append(o);self.data+=data;return i
 def attr(self,arr,typ):
  arr=np.asarray(arr,dtype='<f4'); i=len(self.g['accessors']);o={'bufferView':self.blob(arr.tobytes(),34962),'componentType':5126,'count':len(arr),'type':typ,'min':arr.min(axis=0).tolist(),'max':arr.max(axis=0).tolist()};self.g['accessors'].append(o);return i
 def write(self,path):
  self.data+=b'\0'*((-len(self.data))%4);self.g['buffers'][0]['byteLength']=len(self.data)
  j=json.dumps(self.g,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4)
  out=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(self.data))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(self.data),0x004e4942)+self.data
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)
def dae(item):
 p=root/item['source'];t=ET.parse(p).getroot();out=GLB(item)
 assert sub(t,'c:asset/c:up_axis').text=='Z_UP','Unrecognized source axes'
 unit=float(sub(t,'c:asset/c:unit').attrib['meter']);assert unit==1,'Explicit unit handling needed'
 images={im.attrib['id']:sub(im,'c:init_from').text for im in many(t,'c:library_images/c:image')}
 effects={}; mats={}
 for e in many(t,'c:library_effects/c:effect'):
  profile=sub(e,'c:profile_COMMON');phong=sub(profile,'c:technique/c:phong')
  if phong is None:phong=sub(profile,'c:technique/c:lambert')
  assert phong is not None
  diffuse=sub(phong,'c:diffuse');m={'name':e.attrib['id'],'pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':1}}
  c=sub(diffuse,'c:color'); tex=sub(diffuse,'c:texture')
  if c is not None:m['pbrMetallicRoughness']['baseColorFactor']=numbers(c.text).tolist()
  if tex is not None:
   sampler=next(x for x in many(profile,'c:newparam') if x.attrib['sid']==tex.attrib['texture']);surface=sub(sampler,'c:sampler2D/c:source').text
   surface=next(x for x in many(profile,'c:newparam') if x.attrib['sid']==surface);im=sub(surface,'c:surface/c:init_from').text;path=p.parent/images[im];data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
   ii=len(out.g.setdefault('images',[]));out.g['images'].append({'name':im,'mimeType':'image/png','bufferView':out.blob(data),'extras':{'source_sha256':hashlib.sha256(data).hexdigest()}})
   ti=len(out.g.setdefault('textures',[]));out.g['textures'].append({'source':ii});m['pbrMetallicRoughness']['baseColorTexture']={'index':ti}
  shin=sub(phong,'c:shininess/c:float')
  if shin is not None:m['pbrMetallicRoughness']['roughnessFactor']=float(np.sqrt(2/(2+max(0,float(shin.text)))))
  effects[e.attrib['id']]=len(out.g['materials']);out.g['materials'].append(m)
 for m in many(t,'c:library_materials/c:material'):mats[m.attrib['id']]=effects[sub(m,'c:instance_effect').attrib['url'][1:]]
 geometries={};sourcepoints={}
 for ge in many(t,'c:library_geometries/c:geometry'):
  mesh=sub(ge,'c:mesh');sources={}
  for s in many(mesh,'c:source'):
   ac=sub(s,'c:technique_common/c:accessor');a=numbers(sub(s,'c:float_array').text);stride=int(ac.attrib.get('stride',1));count=int(ac.attrib['count']);offset=int(ac.attrib.get('offset',0));sources[s.attrib['id']]=a[offset:offset+stride*count].reshape(count,stride)
  verts={v.attrib['id']:{i.attrib['semantic']:i.attrib['source'][1:] for i in many(v,'c:input')} for v in many(mesh,'c:vertices')}
  primitives=[];positions=[]
  for tri in mesh:
   tag=tri.tag.split('}')[-1]
   if tag in ('source','vertices'):continue
   assert tag in ('triangles','polylist'),f'Unsupported primitive {tag} in {p}'
   inputs=many(tri,'c:input');stride=max(int(i.attrib.get('offset',0)) for i in inputs)+1;idx=numbers(sub(tri,'c:p').text).astype(np.int64).reshape(-1,stride)
   if tag=='polylist':
    counts=numbers(sub(tri,'c:vcount').text).astype(int);assert len(counts)==int(tri.attrib['count']);faces=[];cursor=0
    for count in counts:
     assert count>=3
     for k in range(1,count-1):faces.extend([idx[cursor],idx[cursor+k],idx[cursor+k+1]])
     cursor+=count
    assert cursor==len(idx);idx=np.asarray(faces)
   else:assert len(idx)==int(tri.attrib['count'])*3
   attrs={}
   for ip in inputs:
    sem=ip.attrib['semantic'];src=ip.attrib['source'][1:];offset=int(ip.attrib.get('offset',0))
    if sem=='VERTEX':src=verts[src]['POSITION'];sem='POSITION'
    ar=sources[src][idx[:,offset]].copy()
    if sem=='TEXCOORD':ar[:,1]=1-ar[:,1];name='TEXCOORD_'+ip.attrib.get('set','0');typ='VEC2';ar=ar[:,:2]
    elif sem=='COLOR':name='COLOR_'+ip.attrib.get('set','0');typ='VEC'+str(ar.shape[1])
    elif sem in ('POSITION','NORMAL'):name=sem;typ='VEC3';ar=ar[:,:3]
    else:raise RuntimeError('Unknown attribute '+sem)
    attrs[name]=out.attr(ar,typ)
    if sem=='POSITION':positions.append(ar)
   material=tri.attrib.get('material');prim={'attributes':attrs,'mode':4}
   if material:prim['material']=mats[material]
   primitives.append(prim);out.triangles+=len(idx)//3
  geometries[ge.attrib['id']]=len(out.g['meshes']);out.g['meshes'].append({'name':ge.attrib.get('name',ge.attrib['id']),'primitives':primitives});sourcepoints[ge.attrib['id']]=np.concatenate(positions)
 scene_id=sub(t,'c:scene/c:instance_visual_scene').attrib['url'][1:];scene=next(s for s in many(t,'c:library_visual_scenes/c:visual_scene') if s.attrib['id']==scene_id)
 def node(n,parent_transform):
  mat=ident()
  for x in n:
   tag=x.tag.split('}')[-1]
   if tag=='matrix':mat=mat @ numbers(x.text).reshape(4,4)
   elif tag=='translate':a=ident();a[:3,3]=numbers(x.text);mat=mat @ a
   elif tag=='scale':a=ident();a[np.arange(3),np.arange(3)]=numbers(x.text);mat=mat @ a
   elif tag=='rotate':
    a=numbers(x.text);axis=a[:3]/np.linalg.norm(a[:3]);theta=np.deg2rad(a[3]);K=np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]]);R=ident();R[:3,:3]=np.eye(3)+np.sin(theta)*K+(1-np.cos(theta))*K@K;mat=mat @ R
  world=parent_transform @ mat;obj={'name':n.attrib.get('name',n.attrib.get('id','node')),'matrix':mat.T.reshape(-1).tolist()};idx=len(out.g['nodes']);out.g['nodes'].append(obj)
  instances=many(n,'c:instance_geometry');assert len(instances)<=1
  if instances:
   gid=instances[0].attrib['url'][1:];obj['mesh']=geometries[gid];pos=sourcepoints[gid];pts=pos@world[:3,:3].T+world[:3,3];out.bounds.append(pts)
  children=[node(c,world) for c in many(n,'c:node')]
  if children:obj['children']=children
  return idx
 out.g['scenes'][0]['nodes']=[node(n,ident()) for n in many(scene,'c:node')];return out

def stl(item):
 p=root/item['source'];d=p.read_bytes();n=struct.unpack_from('<I',d,80)[0];assert len(d)==84+50*n
 rows=np.frombuffer(d,offset=84,dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attr','<u2')]),count=n)
 pos=rows['v'].reshape(-1,3);nor=np.repeat(rows['normal'],3,axis=0);o=GLB(item);o.g['materials']=[{'name':'Uncolored source STL; neutral display material','pbrMetallicRoughness':{'baseColorFactor':[0.45,0.45,0.45,1],'metallicFactor':0,'roughnessFactor':0.8}}]
 o.g['meshes']=[{'name':item['link'],'primitives':[{'attributes':{'POSITION':o.attr(pos,'VEC3'),'NORMAL':o.attr(nor,'VEC3')},'material':0,'mode':4}]}];o.g['nodes']=[{'name':item['link'],'mesh':0}];o.g['scenes'][0]['nodes']=[0];o.bounds=[pos];o.triangles=n;return o

def main():
 report=[]
 for item in json.loads((root/'conversion-plan.json').read_text()):
  o=dae(item) if item['source'].endswith('.dae') else stl(item);out=root/'dist'/item['output'];o.write(out);p=np.concatenate(o.bounds)
  report.append({'link':item['link'],'asset':item['output'],'source':item['source'],'bounds_mesh_m':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'triangles':o.triangles,'objects':len(o.g['meshes']),'materials':len(o.g['materials']),'images':len(o.g.get('images',[])),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
  print('EXPORTED',item['link'],o.triangles,report[-1]['bounds_mesh_m'],flush=True)
 (root/'dist/geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
