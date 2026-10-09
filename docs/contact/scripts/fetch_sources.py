import urllib.request,json,pathlib,concurrent.futures,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
commit='0059d4335f8156206f63a35662313385f7ad6d74'
base=f'https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/{commit}/robotiq_2f85/'
tree=json.load(urllib.request.urlopen(f'https://api.github.com/repos/google-deepmind/mujoco_menagerie/git/trees/{commit}?recursive=1'))
paths=[x['path'][len('robotiq_2f85/'):] for x in tree['tree'] if x['type']=='blob' and x['path'].startswith('robotiq_2f85/') and not x['path'].endswith('.png')]
def get(p):
 d=urllib.request.urlopen(base+p).read(); out=root/'assets/robotiq_2f85'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(d);return {'path':p,'url':base+p,'sha256':hashlib.sha256(d).hexdigest()}
files=list(concurrent.futures.ThreadPoolExecutor(8).map(get,paths))
(root/'sources.json').write_text(json.dumps({'menagerie_commit':commit,'source':base,'license':'BSD-2-Clause','files':files},indent=2))
print('Downloaded',len(files),commit)
