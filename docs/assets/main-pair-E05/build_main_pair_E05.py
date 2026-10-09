"""Original two source-anchored main DC routes and retained cable supports.
E04 is immutable. Upstream pack/merge/fuses remain unresolved and unenergized.
"""
from pathlib import Path
import numpy as np,math,json,hashlib,cadquery as cq
import cad_export_E05 as ce
P=Path(__file__).resolve().parent;O=P/'main_routes_E05';O.mkdir(exist_ok=True);ce.P=O
parts=[];routes=[];supports=[];holes=[]
ce.CUSTOM_TESS={}
box,bore,cyl=ce.box,ce.bore,ce.cyl
Q=json.loads((P/'victron_candidate/switchgear_E04/isolator_placement_contract.json').read_text());L=json.loads((P/'victron_candidate/lynx_E04/lynx_mounted_contract.json').read_text());ports={p['id']:p for p in Q['power_terminals']+L['power_terminals']}
def add(n,s,mat='steel',note='Original project hardware; strength, material grade and vibration qualification open.'):
 assert s.isValid(),n;parts.append((n,s,mat,note));return s
def smooth(t):return 10*t**3-15*t**4+6*t**5
def sampled(fn,n=20):return np.array([fn(t)for t in np.linspace(0,1,n+1)])
def makepath(kind):
 pos=kind=='positive';start=np.array(ports['Q0:'+('P_OUT'if pos else'N_OUT')]['wire_mouth_C_mm']);end=np.array(ports['LYNX:BAT'+('+'if pos else'-')]['lug_mouth_C_mm']);sy=start[1];z0=start[2];Rxy=85.2 if pos else 92.;zlong=z0 if pos else 270.;R=math.hypot(Rxy,(zlong-z0)/2);xturn=-1740. if pos else -1685.;segments=[]
 def seg(a,ta,tb):segments.append((np.array(a),ta,tb))
 seg([start,[xturn,sy,z0]],[-1,0,0],[-1,0,0])
 seg(sampled(lambda t:[xturn-R*math.sin(math.pi*t),sy-Rxy*(1-math.cos(math.pi*t)),z0+(zlong-z0)/2*(1-math.cos(math.pi*t))]),[-1,0,0],[1,0,0])
 y0=sy-2*Rxy;targety=-450 if pos else -470.;xs=-1435 if pos else -1660.;seg([[xturn,y0,zlong],[xs,y0,zlong]],[1,0,0],[1,0,0]);ang=math.pi/6 if pos else math.pi/4;rs=(targety-y0)/(2*(1-math.cos(ang)))
 seg(sampled(lambda t:[xs+rs*math.sin(ang*t),y0+rs*(1-math.cos(ang*t)),zlong]),[1,0,0],[math.cos(ang),math.sin(ang),0])
 xmid=xs+rs*math.sin(ang);ymid=y0+rs*(1-math.cos(ang));seg(sampled(lambda t:[xmid+rs*(math.sin(ang)-math.sin(ang*(1-t))),ymid+rs*(math.cos(ang*(1-t))-math.cos(ang)),zlong]),[math.cos(ang),math.sin(ang),0],[1,0,0])
 xend=xs+2*rs*math.sin(ang);xc=end[0]-85.2;seg([[xend,targety,zlong],[xc,targety,zlong]],[1,0,0],[1,0,0]);seg(sampled(lambda t:[xc+85.2*math.sin(math.pi*t/2),targety+85.2*(1-math.cos(math.pi*t/2)),zlong]),[1,0,0],[0,1,0])
 ye=targety+85.2;dy=end[1]-ye;dz=end[2]-zlong;phi=2*math.atan(abs(dz)/dy);rr=dy/(2*math.sin(phi));sgn=1 if dz>0 else -1
 seg(sampled(lambda t:[end[0],ye+rr*math.sin(phi*t),zlong+sgn*rr*(1-math.cos(phi*t))]),[0,1,0],[0,math.cos(phi),sgn*math.sin(phi)])
 ym=ye+rr*math.sin(phi);zm=zlong+sgn*rr*(1-math.cos(phi));seg(sampled(lambda t:[end[0],ym+rr*(math.sin(phi)-math.sin(phi*(1-t))),zm+sgn*rr*(math.cos(phi*(1-t))-math.cos(phi))]),[0,math.cos(phi),sgn*math.sin(phi)],[0,1,0])
 edges=[];mins=[]
 for pts,ta,tb in segments:
  if len(pts)==2:e=cq.Edge.makeLine(cq.Vector(*pts[0]),cq.Vector(*pts[-1]));mins.append(None)
  else:
   e=cq.Edge.makeThreePointArc(cq.Vector(*pts[0]),cq.Vector(*pts[len(pts)//2]),cq.Vector(*pts[-1]));assert e.geomType()=='CIRCLE'
   # Three-point sampled circumradius; source bend limit fixed installation6D.
   radii=[]
   for a,b,c in zip(pts[:-2],pts[1:-1],pts[2:]):
    ab=b-a;bc=c-b;ac=c-a;cr=np.linalg.norm(np.cross(ab,bc));
    if cr>1e-10:radii.append(np.linalg.norm(ab)*np.linalg.norm(bc)*np.linalg.norm(ac)/(2*cr))
   mins.append(min(radii)if radii else None)
  edges.append(e)
 wire=cq.Wire.assembleEdges(edges); pieces=[]
 for kk,(e,(pts,ta,tb)) in enumerate(zip(edges,segments)):
  print('SWEEP',kind,kk,flush=True)
  profile=cq.Wire.makeCircle(7.1,cq.Vector(*pts[0]),cq.Vector(*ta));piece=cq.Solid.sweep(profile,[],e,True,True);assert piece.isValid();pieces.append(piece)
 s=cq.Compound.makeCompound(pieces)
 return s,{'id':'MAIN_'+kind,'from':'Q0:'+('P_OUT'if pos else'N_OUT'),'to':'LYNX:BAT'+('+'if pos else'-'),'domain':'DC_power','cable_candidate':'LAPP0060001 70mm² black, positive identification required','source_OD_mm':14.2,'source_minimum_fixed_bend_R_mm':85.2,'start_C_mm':start.tolist(),'end_C_mm':end.tolist(),'source_blade_XYZ_verified_at_both_devices':True,'lug_mouth_contours_original_assumptions':True,'jacket_endpoint_coordinate_error_mm':0,'centreline_length_mm':wire.Length(),'sampled_min_radius_mm':min(r for r in mins if r is not None),'segment_sampled_radii_mm':mins,'CAD_centreline_edges_are_exact_lines_and_circles':True,'CAD_minimum_circular_radius_mm':min(e.radius()for e in edges if e.geomType()=='CIRCLE'),'points_by_segment_C_mm':[p.tolist()for p,_,_ in segments],'full_terminal_to_terminal_jacket_route':True,'crimped_conductor_contact_proven':False,'energizable_circuit':False,'upstream_protection_and_merge_installed':False,'cable_thermal_ampacity_and_voltage_drop_qualified':False}
for kind in ['positive','negative']:
 print('BEGIN_ROUTE',kind,flush=True);s,r=makepath(kind);print('ROUTE_READY',kind,flush=True);add('MAIN_'+kind+'_70mm2_routed_jacket',s,'housing','Source14.2mm jacket envelope; end-to-end lug mouths, not conductor/crimp reconstruction. Black cable positive marking still required.');routes.append(r);ce.CUSTOM_TESS['MAIN_'+kind+'_70mm2_routed_jacket']=ce.route_mesh(r)
 pos=kind=='positive';y=-450 if pos else -470;z=184.25 if pos else 270
 for i,x in enumerate([-975,-650,-350,260]if pos else[-925,-700,-300,310]):
  stem=f'MAIN_{kind}_support{i}';lower=box(20,40,10,(x,y,z-5));upper=box(20,40,10,(x,y,z+5));axis=cq.Workplane('YZ').center(y,z).circle(7.1).extrude(24).translate((x-12,0,0)).val();lower=lower.cut(axis);upper=upper.cut(axis)
  stand=box(30,50,3,(x,y,104.5)).fuse(box(4,40 if pos else 20,z-119,(x,y,(106+z-13)/2))).fuse(box(30,50,3,(x,y,z-11.5)))
  for j,yy in enumerate([y-14,y+14]):
   lower=bore(lower,x,yy,2.2,z-11,12);upper=bore(upper,x,yy,2.2,z-1,12);stand=bore(stand,x,yy,2.2,z-14,5);stand=stand.cut(cyl(5,9,(x,yy,z-22)))
   under=z+10.8;shaft=cyl(2,30,(x,yy,under-30));head=cyl(3.5,4,(x,yy,under));add(stem+f'_M4x30_{j}',shaft.fuse(head))
   for wn,wz in [('upper',z+10),('lower',z-13.8)]:add(stem+f'_{wn}_washer_{j}',cq.Workplane('XY').circle(4.5).circle(2.2).extrude(.8).translate((x,yy,wz)).val())
   add(stem+f'_M4nut_{j}',cq.Workplane('XY').polygon(6,7/math.cos(math.pi/6)).circle(2).extrude(3.2).translate((x,yy,z-17)).val())
  add(stem+'_welded_stand',stand,'steel','Original aluminium stand at deckZ103 with30×50foot,4mmweb and3mmshelf. Same-alloy deck weld proposal; strength and metallurgy unqualified. Colour not material proof.');add(stem+'_lower_clamp',lower,'cover','Original split clamp, nominal14.2mm bore; actual liner/material/compression/pullout unqualified.');add(stem+'_upper_clamp',upper,'cover','Original retained split clamp; nominal clearance-free cable jacket interface only.')
  supports.append({'id':stem,'axis_C_mm':[x,y,z],'cable_axis_C':[1,0,0],'body_support':'main_base_deck_3mm','foot_plane_Z_mm':103,'weld_foot_mm':[30,50],'two_bolts':'M4x30, nominal0.7thread','nut_engagement_mm':3.2,'thread_protrusion_mm':2.2,'cable_pullout_vibration_thermal_qualified':False})
# Four real source-sizeM25 partition glands. Panel3+nut6 consumes9of10mm thread.
for target,x in [('controller_battery_partition',-1143),('battery_tool_partition',-460)]:
 for kind,y,z in [('positive',-450,184.25),('negative',-470,270)]:
  stem=f'MAIN_{kind}_{target}_gland';tf=lambda s:s.rotate((0,0,0),(0,1,0),-90).translate((x,y,z))
  thread=cq.Workplane('XY').circle(12.5).circle(8.5).extrude(10).translate((0,0,-10)).val();body=cq.Workplane('XY').polygon(6,30/math.cos(math.pi/6)).circle(8.5).extrude(6).val().intersect(cyl(16.8,6,(0,0,0)));cap=cq.Workplane('XY').circle(16.8).circle(7.1).extrude(24).translate((0,0,6)).val()
  add(stem+'_LAPP53111030',tf(thread.fuse(body).fuse(cap)),'cover','SourceM25×1.5,SW30,Ø33.6,10mmthread,max40overall,8..17cable. Internal clamp contours original; no installedIPclaim.')
  nut=cq.Workplane('XY').polygon(6,34/math.cos(math.pi/6)).circle(12.5).extrude(6).translate((0,0,-9)).val().intersect(cyl(18.7,6,(0,0,-9)));add(stem+'_LAPP53119030',tf(nut),'cover','SourceM25×1.5 SW34,Ø37.4,6mm thickness; nominal cylindrical threadcontact,1mm protrusion.')
  holes.append({'target_part':target,'center_C_mm':[x+1.5,y,z],'axis_C':[1,0,0],'diameter_mm':25.2,'cut_X_mm':[x-1,x+4],'gland_panel_seat_X_mm':x,'panel_thickness_mm':3,'nut_thickness_mm':6,'source_thread_length_mm':10,'source_thread_engagement_mm':6})
meta=ce.export('main_pair_supported_E05',parts,{'source':'Original supported main DC cable routes; LAPP fixed cable and glands source dimensions; existing ABB/Lynx source terminal anchors','vehicle_placed':True})
out={'revision':'E05_candidate','geometry':meta,'parts':[{'name':n,'solids':len(s.Solids()),'volume_mm3':s.Volume()}for n,s,_,_ in parts],'routes':routes,'supports':supports,'partition_hole_patch':holes,'existing_E04_overlays_to_remove':['Q0_P_OUT_service_lead_bend','Q0_N_OUT_service_lead_bend'],'source_urls':['https://products.lappgroup.com/fileadmin/documents/technische_doku/datenblaetter/skintop/DB53111000EN.pdf','https://products.lappgroup.com/fileadmin/documents/technische_doku/datenblaetter/skintop/DB53119000EN.pdf','https://lapp.com.ph/products/53119030'],'required_geometry_checks_passed':False,'freeze':False,'remaining_upstream_gates':['≤100A covered pack fuses/source mount andterminal datums','Source-rated retainedpositive/negativemerge','Main positivefuse andcoordination','Battery installedpolarity andterminalrevision'],'no_motor_port_invented':True,'electrical_operational_acceptance':False}
(O/'main_pair_contract_E05.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'parts':len(parts),'routes':[{'id':r['id'],'length_mm':r['centreline_length_mm'],'min_sampled_R_mm':r['sampled_min_radius_mm']}for r in routes]}))
