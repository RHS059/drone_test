import pathlib,xml.etree.ElementTree as ET,json
import cadquery as cq
R=pathlib.Path(__file__).resolve().parents[1]
# Original analytic coupon, CAD files in mm; MJCF uses metres.
coupon=cq.Workplane('XY').box(40,40,30)
cq.exporters.export(coupon,str(R/'assets/coupon_40x40x30_mm.step'))
cq.exporters.export(coupon,str(R/'assets/coupon_40x40x30_mm.stl'))
cases=[dict(id='nominal',mass_kg=.15,friction=.7),dict(id='low-friction',mass_kg=.15,friction=.015),dict(id='heavy',mass_kg=2.,friction=.7)]
for case in cases:
 tree=ET.parse(R/'assets/robotiq_2f85/2f85.xml');root=tree.getroot()
 root.set('model','reconstructed_contact_'+case['id'])
 root.find('compiler').set('meshdir','robotiq_2f85/assets')
 opt=root.find('option');opt.set('timestep','0.001');opt.set('gravity','0 0 -9.81');opt.set('integrator','implicitfast');opt.set('iterations','100');opt.set('tolerance','1e-10')
 world=root.find('worldbody');mount=world.find('body');mount.set('pos','0 0 0.3');mount.set('quat','0 1 0 0');mount.set('mocap','true')
 ET.SubElement(world,'geom',name='floor',type='plane',size='1 1 .01',rgba='.16 .19 .23 1')
 obj=ET.SubElement(world,'body',name='coupon',pos='0 0 0.1512')
 ET.SubElement(obj,'freejoint',name='coupon_free')
 ET.SubElement(obj,'geom',name='coupon_collision',type='box',size='.02 .02 .015',mass=str(case['mass_kg']),friction=f"{case['friction']} .005 .0001",priority='2',rgba='.95 .57 .15 1',condim='4')
 ET.SubElement(root.find('equality'),'weld',name='initial_world_fixture',body1='coupon',solref='.002 1')
 tree.write(R/f"assets/{case['id']}.xml",encoding='unicode')
scenario={'reconstruction':True,'native_version':'3.15.0','wasm_version':'3.15.0','duration_s':5.5,'dt_s':.001,'sample_stride':10,'sample_count':550,'fixture_release_s':1.5,'gripper_release_s':4.0,'move_start_s':2.,'move_end_s':3.5,'target_x_m':.1,'initial_coupon_center_m':[0,0,.1512],'strict_position_tolerance_m':.01,'case_parameters':cases,'control':{'open_ctrl':0,'closed_ctrl':200,'close_start_s':.2,'close_end_s':1.2},'notes':['New declared reconstruction; historical exact parameters unavailable.','The only coupon weld is an explicitly labeled temporary world fixture, disabled at 1.5 seconds. No object-to-gripper weld.','Mesh source millimetres scaled 0.001 by Menagerie. Coupon STEP/STL millimetres; analytic box collision half sizes metres.','Strict task positioning error is max Euclidean coupon-target error over 1.6 <= time < 4.0 s; release is separately checked.','Transport trajectory is prescribed gripper base motion; contacts and object rigid-body dynamics are solved. No full arm/UGV/controller simulation.']}
(R/'scenario.json').write_text(json.dumps(scenario,indent=2))
