"""Original C02 interface hardware, NOT OEM CAD. MM. Development only.
Plate local XY is bolt plane, +Z is into rover; adapter +Z is outboard.
No drive mesh/STEP from the commercial manufacturer is redistributed.
"""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'mechanical'))
from generate_cad import glb,properties,exact_bounds
import cadquery as cq
P=Path(__file__).resolve().parent
HOLES=[(-113,0),(113,0),(-101.823376,-49),(101.823376,-49),(-101.823376,49),(101.823376,49),(-66.992537,91),(66.992537,91)]
def export(s,name,notes):
 assert s.isValid() and len(s.Solids())==1
 cq.exporters.export(s,str(P/(name+'.step')))
 # Interface-local model uses CAD X/Y/Z; assembly conversion supplied in contract.
 glb([(name,s)],P/(name+'.glb'))
 r={'part':name,'original_geometry':True,'not_vendor_CAD':True,'not_fabrication_released':True,'bounds_mm':exact_bounds(s),'solid_count':len(s.Solids()),'BRep_valid':s.isValid(),'density_kg_m3':7850,'density_assumed':True,**properties(s),'notes':notes}
 (P/(name+'_report.json')).write_text(json.dumps(r,indent=2));print(name,r['mass_kg'],flush=True)
 return r

def upright():
 outline=[(-145,-130),(-90,-150),(-75,-205),(75,-205),(90,-150),(145,-130),(145,130),(90,150),(75,205),(-75,205),(-90,150),(-145,130)]
 p=cq.Workplane('XY').polyline(outline).close().extrude(18)
 p=p.cut(cq.Workplane('XY').circle(86).extrude(20))
 for x,y in HOLES:p=p.cut(cq.Workplane('XY').center(x,y).circle(4.25).extrude(20))
 # Original clevis ears: axis X, y +/-170, z=-15, original joint geometry.
 for sign in [-1,1]:
  for x in [-59,59]:
   ear=cq.Workplane('XY').box(8,60,53).translate((x,sign*170,-8.5)) # z[-35,18]
   pin=cq.Workplane('YZ').center(sign*170,-15).circle(10.25).extrude(80,both=True)
   p=p.union(ear.cut(pin))
 # Through-window clears both outer eye barrels and converging arm tubes.
 for sign in [-1,1]:
  pocket=cq.Workplane('YZ').center(sign*170,-15).circle(60).extrude(55,both=True)
  p=p.cut(pocket)
 return export(p.val(),'upright_WD220_C02_R04',{'mount_pattern_mm':HOLES,'pattern_source':'verified asymmetric commercial STEP hole axes; drawing checked separately','motor_socket_diameter_mm':172,'motor_socket_fit':'nominal only, finished fit unselected','eight_holes':'Ø8.5 pilots intended M10x1.5; not finished threads','plate_mm':18,'outer_joint_centers_local_mm':[[0,170,-15],[0,-170,-15]],'joint_pin_axis_local':[1,0,0],'clevis_bore_mm':20.5,'no_steering':'upright held by parallel links; steering mechanism unimplemented','manufacturing':'welded/finish-machined original carrier; welds/fillets/grade/fasteners unqualified'})

def adapter():
 p=cq.Workplane('XY').circle(110).circle(47).extrude(30)
 p=p.union(cq.Workplane('XY').circle(57.05).circle(47).extrude(10).translate((0,0,30)))
 incoming=[];outgoing=[]
 for a in range(0,360,72):
  x,y=70*math.cos(math.radians(a)),70*math.sin(math.radians(a));incoming.append([x,y])
  p=p.cut(cq.Workplane('XY').center(x,y).circle(8.5).extrude(42))
  # Socket pockets continue through pilot, producing intentional segmented centering lands.
  p=p.cut(cq.Workplane('XY').center(x,y).circle(18).extrude(32).translate((0,0,10)))
 for a in range(36,396,72):
  x,y=82.55*math.cos(math.radians(a)),82.55*math.sin(math.radians(a));outgoing.append([x,y])
  p=p.cut(cq.Workplane('XY').center(x,y).circle(7).extrude(32))
 return export(p.val(),'wheel_adapter_C02_R01',{'drive_input_pattern':'5xØ17 clearance onØ140PCD phase0deg for sourceM16x1.5 studs','output_pattern':'5xØ14 tap-drill pilots onØ165.1PCD phase36deg intendedM16x1.5 studs; finished threads absent','input_centers_mm':incoming,'output_centers_mm':outgoing,'WD220_pilot_socket_mm':94,'EVO_pilot_lands_nominal_mm':114.1,'pilot_protrusion_mm':10,'face_spacing_mm':30,'input_socket_pockets':'Ø36 fromZ10 throughZ40 to preserve nut/socket approach; segmented outputpilot','fits':'all nominal, tolerances/retention not released','output_studs':'not modeled; actual rim thickness, closed nut cavity/engagement and stud length unresolved','load_path':'wheel rim->adapter studs/contact->drive flange; strength/torque/fatigue not validated','material':'steel7850kg/m3 assumption, not approvedgrade'})
if __name__=='__main__':upright();adapter()

# The following parts are original, unqualified C02 wishbone hardware; no vendor internals.
def cyl_axis(radius,length,origin,axis,inner=0):
 w=cq.Workplane(cq.Plane(origin=tuple(float(v) for v in origin),normal=tuple(float(v) for v in axis))).circle(radius)
 if inner:w=w.circle(inner)
 return w.extrude(length)
def tube_between(a,b,ro=16,ri=13):
 import numpy as np
 a,b=np.array(a,float),np.array(b,float);v=b-a;L=float(np.linalg.norm(v));return cyl_axis(ro,L,a,v/L,ri)
def arm(z,lower=False):
 eyes=[(-170,550,z),(170,550,z),(0,812,z-150)]
 solids=[]
 for i,(x,y,zz) in enumerate(eyes):
  length=80 if i<2 else 100
  solids.append(cyl_axis(25,length,(x-length/2,y,zz),(1,0,0)))
 p=solids[0].union(solids[1]).union(solids[2])
 for a in eyes[:2]:
  if lower:
   mid=((a[0])/2,681,z-95)
   p=p.union(tube_between(a,mid)).union(tube_between(mid,eyes[2]))
  else:p=p.union(tube_between(a,eyes[2]))
 for x,y,zz in eyes:p=p.cut(cyl_axis(17.5,110,(x-55,y,zz),(1,0,0)))
 if lower:
  # Crossbrace halves and a real open clevis, not a solid bar occupying shock-eye space.
  y,zz=550+.65*262,z-.65*150
  for a,b in [((-59.5,y,zz),(-24,y,zz)),((24,y,zz),(59.5,y,zz))]:p=p.union(tube_between(a,b,20,16))
  for x in [-20,20]:
   ear=cq.Workplane('XY').box(8,40,40).translate((x,y,zz)).cut(cyl_axis(7.25,20,(x-10,y,zz),(1,0,0)))
   p=p.union(ear)
 return p.val()

def fixed_mount():
 # Actual split rail clamp; rail unchanged. Inner backing pad is a separate removable part.
 poly=[(-235,-320),(235,-320),(235,90),(180,130),(40,130),(40,200),(-40,200),(-40,130),(-180,130),(-235,90)]
 # Define in XZ; + extrusion points inward along -Y.
 p=cq.Workplane('XZ',origin=(0,522,0)).polyline(poly).close().extrude(12)
 # Weight relief away from tie-bolt and root-clevis load paths; not strength approved.
 for zz in [-235,-40]:
  opening=cq.Workplane('XZ',origin=(0,530,0)).center(0,zz).rect(300,80).extrude(30)
  p=p.cut(opening)
 for x in [-35,35]:
  for zz in [-114,114]:p=p.cut(cyl_axis(6.5,30,(x,505,zz),(0,1,0)))
 for rootz in [70,-270]:
  for rootx in [-170,170]:
   for dx in [-49,49]:
    ear=cq.Workplane('XY').box(8,58,60).translate((rootx+dx,551,rootz))
    ear=ear.cut(cyl_axis(10.25,30,(rootx+dx-15,550,rootz),(1,0,0)))
    p=p.union(ear)
 # Upper shock clevis on narrow tower, open between x=-16 and+16.
 for x in [-20,20]:
  ear=cq.Workplane('XY').box(8,68,60).translate((x,556,170))
  ear=ear.cut(cyl_axis(7.25,20,(x-10,560,170),(1,0,0)))
  p=p.union(ear)
 backing=cq.Workplane('XY').box(100,12,260).translate((0,404,0))
 for x in [-35,35]:
  for zz in [-114,114]:backing=backing.cut(cyl_axis(6.5,30,(x,390,zz),(0,1,0)))
 return p.val(),backing.val()

def build_wishbones():
 p,back=fixed_mount()
 for name,s in [('stationary_clamp_C02_R01',p),('inner_backing_C02_R01',back),('upper_wishbone_C02_R02',arm(70)),('lower_wishbone_C02_R02',arm(-270,True))]:
  export(s,name,{'axes':'already vehicleC mm atstationX0,leftside','design':'original welded CHS32x3 tube link withØ50 eyes/Ø35nominal bearing pockets, chosenGE20ESenvelope20x35x16','status':'fits,retainers,pins,grade,welds,stiffness,fatigue andloadselection unresolved'})

if __name__=='__main__':build_wishbones()

def export_group(parts,name,notes):
 assert all(s.isValid() for _,s in parts)
 ass=cq.Assembly(name=name)
 for n,s in parts:ass.add(s,name=n)
 ass.export(str(P/(name+'.step')));glb(parts,P/(name+'.glb'))
 comp=cq.Compound.makeCompound([s for _,s in parts]);r={'group':name,'count':len(parts),'all_BRep_valid':True,'bounds_mm':exact_bounds(comp),'density_assumption_kg_m3':7850,**properties(comp),'notes':notes}
 (P/(name+'_report.json')).write_text(json.dumps(r,indent=2));print(name,r['mass_kg'],flush=True)

def pin_x(x,y,z,length=130,head_radius=16):
 p=cyl_axis(10,length,(x-length/2,y,z),(1,0,0)).union(cyl_axis(head_radius,6,(x-length/2-6,y,z),(1,0,0)))
 p=p.cut(cyl_axis(2,40,(x+length/2-7,y-20,z),(0,1,0)))
 return p.val()
def hardware():
 parts=[]
 for rootz in [70,-270]:
  for rootx in [-170,170]:parts.append((f'original_hinge_pin_{rootx}_{rootz}',pin_x(rootx,550,rootz)))
 # Nominal fastener geometry, not a particular purchased manufacturer's model; cosmetic threads omitted.
 for x in [-35,35]:
  for z in [-114,114]:
   bolt=cyl_axis(6,140,(x,398,z),(0,1,0))
   head=cq.Workplane(cq.Plane(origin=(x,390.5,z),normal=(0,1,0))).polygon(6,18/math.cos(math.pi/6)).extrude(7.5)
   parts.append((f'M12_nominal_clamp_bolt_{x}_{z}',bolt.union(head).val()))
   parts.append((f'M12_nominal_washer_{x}_{z}',cyl_axis(12,2,(x,522,z),(0,1,0),6.5).val()))
   nut=cq.Workplane(cq.Plane(origin=(x,524,z),normal=(0,1,0))).polygon(6,18/math.cos(math.pi/6)).circle(6).extrude(10)
   parts.append((f'M12_nominal_nut_{x}_{z}',nut.val()))
 export_group(parts,'stationary_hardware_C02_R01',{'status':'Original hinge pins and nominal M12 fastener envelopes. Grade, torque, locking/cotter hardware and fit not approved. No helical threads modeled.'})
 pins=[('outer_upper_hinge_pin',pin_x(0,812,-80,150,13)),('outer_lower_hinge_pin',pin_x(0,812,-420,150,13))]
 export_group(pins,'upright_pins_C02_R02',{'coordinates':'vehicleC,leftstation0; translatewithupright; no yawsteering'})
 for label,z in [('upper',70),('lower',-270)]:
  bearings=[]
  for x,y,zz,L in [(-170,550,z,80),(170,550,z,80),(0,812,z-150,100)]:
   for d in [-1,1]:
    center=x+d*(L/2-8)
    bearings.append((f'GE20ES_fit_envelope_{x}_{d}',cyl_axis(17.5,16,(center-8,y,zz),(1,0,0),10).val()))
  export_group(bearings,label+'_bearing_envelopes_C02_R02',{'NOT_physical_bearing_model':True,'reference_only':'GE20ESnominal20x35x16outerfit-envelope; no invented races or internal geometry','mass_warning':'computed filled-envelope mass MUST NOT be used as purchased bearing mass','retention':'not resolved'})
if __name__=='__main__':hardware()
