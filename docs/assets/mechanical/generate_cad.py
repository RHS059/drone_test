"""Original R06 CAD reconstruction, not recovery of R04. Units mm, X forward/Y left/Z up.
Run: python generate_cad.py (CadQuery 2.7, numpy). Outputs into this directory.
Manufacturing-development geometry only: see QUALIFICATION.md.
"""
from pathlib import Path
import cadquery as cq
import numpy as np
import json, math, struct, csv
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def exact_bounds(s):
    b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return b.Get()
P=Path(__file__).resolve().parent
DENSITY=7850 # kg/m3 assumed steel; grade unspecified

def box(x,y,z,c): return cq.Workplane('XY').box(x,y,z).translate(c)
def rhs(axis,length,width,height,t,center,ro=20):
    dims=(length,width,height) if axis=='X' else (width,length,height)
    ins=(length+2,width-2*t,height-2*t) if axis=='X' else (width-2*t,length+2,height-2*t)
    outer=box(*dims,center).edges('|'+axis).fillet(ro)
    inner=box(*ins,center).edges('|'+axis).fillet(ro-t)
    return outer.cut(inner).val(),outer.val()

def glb(parts,path):
    """Write explicit metres/Z-up vertex data, no implicit root rotation."""
    data=bytearray(); views=[]; acc=[]; meshes=[]; nodes=[]
    def buf(a,typ,comp):
        a=np.asarray(a,dtype=np.float32 if comp==5126 else np.uint32)
        while len(data)%4:data.append(0)
        off=len(data); data.extend(a.tobytes()); vi=len(views); views.append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes})
        idx=len(acc); ac={'bufferView':vi,'componentType':comp,'count':len(a),'type':typ}
        if typ=='VEC3': ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
        acc.append(ac);return idx
    for name,s in parts:
        verts,tris=s.tessellate(.2,.1); v=np.array([[p.x,p.y,p.z] for p in verts],dtype=float)/1000;f=np.array(tris,dtype=np.uint32)
        # Separate faces for robust flat shading independent of shared OCC vertices.
        v=v[f].reshape(-1,3); normals=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]); norms=np.linalg.norm(normals,axis=1); normals/=np.maximum(norms[:,None],1e-30);normals=np.repeat(normals,3,axis=0)
        pi=buf(v,'VEC3',5126);ni=buf(normals,'VEC3',5126);ii=buf(np.arange(len(v),dtype=np.uint32),'SCALAR',5125)
        meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni},'indices':ii,'material':0}]});nodes.append({'name':name,'mesh':len(meshes)-1})
    doc={'asset':{'version':'2.0','generator':'Original CadQuery R06 reconstruction; metres Z-up'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':[{'name':'assumed steel','pbrMetallicRoughness':{'baseColorFactor':[.27,.36,.40,1],'metallicFactor':.65,'roughnessFactor':.5}}],'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':acc,'extras':{'units':'metres','upAxis':'Z','revision':'new reconstruction'}}
    js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4)
    path.write_bytes(struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(data))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(data),0x004E4942)+data)

def properties(s,density=DENSITY):
    c=s.Center();return {'volume_m3':s.Volume()*1e-9,'mass_kg':s.Volume()*1e-9*density,'com_m':[c.x/1000,c.y/1000,c.z/1000],'inertia_com_kg_m2':(np.array(cq.Shape.matrixOfInertia(s))*density*1e-15).tolist()}

def export(parts,stem):
    ass=cq.Assembly(name=stem)
    for name,s in parts:ass.add(s,name=name)
    ass.export(str(P/(stem+'.step')));glb(parts,P/(stem+'.glb'))
    comp=cq.Compound.makeCompound([s for _,s in parts]);b=comp.BoundingBox();b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax=exact_bounds(comp)
    overlaps=[];contacts=[]
    for i,(a,sa) in enumerate(parts):
        for bb,sb in parts[i+1:]:
            ba,bs=exact_bounds(sa),exact_bounds(sb)
            if any(ba[k+3]<bs[k]-1e-5 or bs[k+3]<ba[k]-1e-5 for k in range(3)):continue
            print('checking',a,bb,flush=True)
            d=sa.distance(sb)
            if d<1e-5:
                vol=sa.intersect(sb).Volume()
                if vol>1e-4:overlaps.append([a,bb,vol])
                else: contacts.append([a,bb,d])
    valid=all(s.isValid() and len(s.Solids())==1 for _,s in parts)
    report={'revision':stem,'new_reconstruction':True,'units':{'STEP':'mm','GLB':'m, Z-up'},'solid_count':len(comp.Solids()),'bbox_m':[(b.xmax-b.xmin)/1000,(b.ymax-b.ymin)/1000,(b.zmax-b.zmin)/1000],'bounds_m':[[b.xmin/1000,b.ymin/1000,b.zmin/1000],[b.xmax/1000,b.ymax/1000,b.zmax/1000]],'valid_single_solids':valid,'positive_volume_intersections_mm3':overlaps,'zero_gap_contacts':contacts,'density_kg_m3':DENSITY,'density_is_assumption':True,'assembly_properties':properties(comp),'parts':[{'name':n,**properties(s)} for n,s in parts],'fabrication_release':False}
    (P/(stem+'_verification.json')).write_text(json.dumps(report,indent=2));assert valid and not overlaps
    return report

def frame():
    parts=[]; envelopes=[]
    for side,y in [('left',460),('right',-460)]:
        s,e=rhs('X',4000,100,200,10,(0,y,0));parts.append(('main_rail_'+side,s));envelopes.append(e)
    xs=[-1950,-1200,-400,750,1050,1300,1650,1950]
    for i,x in enumerate(xs):
        s,_=rhs('Y',860,100,200,10,(x,0,0))
        for e in envelopes:s=s.cut(e)
        parts.append((f'crossmember_{i+1:02d}',s))
    holes=[]
    for side,y in [('left',300),('right',-300)]:
        s=box(400,400,30,(900,y,115))
        for a in range(0,360,60):
            xh=900+105*math.cos(math.radians(a));yh=y+105*math.sin(math.radians(a))
            s=s.cut(cq.Workplane('XY').center(xh,yh).circle(4.25).extrude(32).translate((0,0,99)));holes.append([xh,yh,8.5])
        parts.append(('arm_deck_'+side,s.val()))
    for j,x in enumerate([-1200,-400,1650]):
        for side,sign in [('left',1),('right',-1)]:
            s=cq.Workplane('YZ').polyline([(sign*410,-70),(sign*310,-70),(sign*410,70)]).close().extrude(8).translate((x+50,0,0)).val()
            parts.append((f'gusset_{j+1}_{side}',s))
    r=export(parts,'frame_R06');assert r['solid_count']==18;assert np.allclose(r['bbox_m'],[4,1.02,.23])
    # Verify pilot cylindrical faces analytically in actual B-reps.
    cylindrical=[]
    for name,s in parts:
        if name.startswith('arm_deck'):
            cylindrical.extend([f for f in s.Faces() if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-4.25)<1e-6])
    assert len(cylindrical)==12
    # Contact graph connectivity: every fabricated part must join the weldment.
    reached={parts[0][0]}
    while True:
        nxt=reached|{b for a,b,d in r['zero_gap_contacts'] if a in reached}|{a for a,b,d in r['zero_gap_contacts'] if b in reached}
        if nxt==reached:break
        reached=nxt
    assert len(reached)==18
    r.update(pilot_holes={'count':12,'diameter_mm':8.5,'purpose':'M10x1.5 tap-drill pilot, not finished thread or UR clearance bore','centers_mm':holes},contact_graph_connected=True,tests_passed=['18 valid individual B-rep solids','4m x 1.02m x .23m bounds','12 actual cylindrical through pilot bores','no pairwise positive-volume intersections','zero-gap connected contact graph','mass/inertia recomputed from geometry'])
    (P/'frame_R06_verification.json').write_text(json.dumps(r,indent=2))
    with (P/'frame_R06_cutlist.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['part','material_assumption','stock','quantity','blank_length_mm','note'])
        w.writerow(['main rails','steel grade TBD','RHS 200x100x10 R20 outside/R10 inside',2,4000,'selected radii require supplier confirmation'])
        for i,x in enumerate(xs):w.writerow([f'crossmember_{i+1:02d}','steel grade TBD','RHS 200x100x10 R20/R10',1,860,f'X={x}; CNC cope ends to rail outer surface; approximate central finished span 820'])
        w.writerow(['arm decks','steel grade TBD','400x400x30 plate',2,400,'six Ø8.5 pilots each; post-weld machine/tap/pins not released'])
        w.writerow(['gussets','steel grade TBD','8mm triangular plate 100x140',6,100,'sharp ideal corners; weld edge preparation TBD'])
    print('FRAME',r['assembly_properties'],flush=True)
    return r

def adapter():
    # Exact nominal envelopes, proposed machining features. No proprietary coupling geometry.
    s=cq.Workplane('XY').circle(50).extrude(23.5)
    s=s.union(cq.Workplane('XY').circle(25).extrude(-2.5))
    # Nonlocating design relief for confirmed vendor annular skirt (R31.5..37.5 x3).
    s=s.cut(cq.Workplane('XY').circle(38).circle(31).extrude(3.5).translate((0,0,20)))
    for a in range(0,360,60):
        x,y=40*math.cos(math.radians(a)),40*math.sin(math.radians(a))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(4.25).extrude(25))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(7).extrude(12).translate((0,0,11.5)))
    for a in range(45,405,90):
        x,y=25*math.cos(math.radians(a)),25*math.sin(math.radians(a))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(2.5).extrude(12).translate((0,0,11.5)))
    # Index pin seats intentionally deferred until checked manufacturer orientation is resolved.
    r=export([('original_adapter_nominal_R03',s.val())],'adapter_R03')
    r.update(nominal_total_thickness_mm=26,face_separation_mm=23.5,ur_pilot_protrusion_mm=2.5,ur_pilot_diameter_mm=50,pilot_fit_status='Nominal geometry only; male fit/tolerance NOT selected or approved',M8_clearance_count=6,M8_clearance_diameter_mm=8.5,M8_counterbore_diameter_mm=14,M8_counterbore_depth_mm=12,M6_tap_pilot_count=4,M6_tap_pilot_diameter_mm=5,M6_tap_pilot_depth_mm=12,locating_pin_seats='not modeled pending validated datum/index requirements',thread_representation='tap-drill holes only, threads not cut',release_blockers=['Pilot fit unapproved','Thread effective engagement and drill tip relief unresolved','Index pin orientation/seats unresolved','Screw grade,length,head tooling clearance and torque unresolved','Adapter strength and payload/inertia limit review unresolved','Full vendor assembly swept-volume check pending'])
    skirt=cq.Workplane('XY').circle(37.5).circle(31.5).extrude(3).translate((0,0,20.5)).val()
    assert s.val().intersect(skirt).Volume()<1e-5
    pilots=[f for f in s.val().Faces() if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-2.5)<1e-6]
    assert len(pilots)==4
    heads=[]
    for a in range(0,360,60):
        x,y=40*math.cos(math.radians(a)),40*math.sin(math.radians(a))
        head=cq.Workplane('XY').center(x,y).circle(6.5).extrude(8).translate((0,0,11.5)).val()
        assert s.val().intersect(head).Volume()<1e-5
        assert head.intersect(skirt).Volume()<1e-5
    r.update(coupling_skirt_relief={'inner_radius_mm':31,'outer_radius_mm':38,'depth_mm':3.5,'chosen_nominal_clearance_mm':.5,'status':'original design clearance, NOT manufacturer fit'},coupling_skirt_conservative_envelope_intersection_mm3=0,assumed_M8_head={'diameter_mm':13,'height_mm':8,'count':6,'top_Z_mm':19.5,'minimum_axial_skirt_clearance_mm':1,'status':'nominal ISO4762 size envelope; actual hardware/tolerance/length unapproved'},tests_passed=['valid single B-rep solid','26mm total axial envelope','4 actual Ø5 M6 tap pilots','nominal vendor skirt conservative envelope has no intersection','six nominal M8 head envelopes clear adapter and skirt'])
    (P/'adapter_R03_verification.json').write_text(json.dumps(r,indent=2))
    print('ADAPTER',r['assembly_properties'],flush=True)
    return r

if __name__=='__main__':
    frame()
    adapter()
