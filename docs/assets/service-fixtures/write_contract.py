from pathlib import Path
import json
P=Path(__file__).resolve().parent
p=json.loads((P/'parameters.json').read_text())
contract={
 'revision':'S01','corner_contract_revision':'C02_R05','wheel_adapter_revision':'C02_R02','status':'ORIGINAL STATIC WORKHOLDING DEVELOPMENT; NOT FABRICATION RELEASED','safe_working_load_kg':None,'not_lifting_equipment':True,'commercial_stand_ratings_apply':False,
 'axes':'C: X forward, Y left, Z up','units':{'STEP':'mm','GLB':'m'},
 'assets':[
  {'file':'chassis_trestles_S01.glb','group':'chassis_support','transform':'Already C, no scaling or repositioning relative to frame R07'},
  {'file':'corner_cradle_S01.glb','group':'corner_cradle','transform':'Already C left-middle C02 q=0; right side proper Rz(pi); then translate station X −1.35/0/+1.35 m'}],
 'illustrative_floor_Z_C_m':-.78815,'illustrative_chassis_raise_from_C01_nominal_m':.1,'static_pose_only':True,'end_station_floor_foot_nominal_Y_gap_mm':5,'end_station_foot_clearance_status':'Nominal geometry only; placement tolerance and load deflection are not cleared.',
 'chassis_bearing_points_C_m':[[x/1000,y/1000,-.1]for x in p['support_stations_X_mm']for y in p['rail_centers_Y_mm']],
 'saddle_dimensions_mm':[160,220,16],'R07_bottom_flat_contact_width_mm':76,'crossbeam_plate_built_box_dimensions_mm':[200,1300,100,6],
 'chassis_load_path':'R07 main-rail bottom flat → original saddle → transverse box → two vertical boxes → floor plates → qualified floor. Side locator friction is NOT the gravity path or an uplift restraint.',
 'corner_load_path':'Tire tread → replaceable liners → original contour-shoe weldments → cross/longitudinal members → four floor plates. Full corner retention and tipping are NOT qualified.',
 'C02_removable_boundary':['wheel_C01 tire/rim','wheel_adapter_C02_R02','drive representation (no private geometry bundled)','upright_WD220_C02_R04'],
 'pin_nodes_remove_first':['outer_upper_hinge_pin','outer_lower_hinge_pin'],
 'C02_retained_assets':['stationary_clamp_C02_R01','inner_backing_C02_R01','stationary_hardware_C02_R01','upper_wishbone_C02_R02','lower_wishbone_C02_R02','upper_bearing_envelopes_C02_R02','lower_bearing_envelopes_C02_R02'],
 'C02_retained_on_chassis':['stationary rail clamps/backing/tie bolts','upper wishbone','lower wishbone','planned coilover'],
 'pin_removal_interfaces':[{'axis_C':[1,0,0],'center_C_m':[0,.812,-.08]},{'axis_C':[1,0,0],'center_C_m':[0,.812,-.42]}],
 'checked_pin_extraction_corridor':{'radius_m':.014,'X_span_C_m':[-.26,.26],'warning':'Clearance envelope only; pin retention and actual extraction tool not selected.'},
 'cradle_insertion_configuration':{'remove_first':['four capture-post weldments including base plates, upper caps and upper captive nuts','two removable upper crossbars','eight M10-style post-base bolts and washers','four M12-style upper bolts and washers'],'retain':['lower floor frame','contour shoes and liners','eight lower rail captive nuts'],'reason':'Tall posts cannot pass laterally through tire during insertion; install them after unloaded cradle is positioned and module is supported.'},
 'service_sequence_file':'README.md#bounded-c02-removal-and-inspection-sequence',
 'blocked_operations':[
  'Initial lifting: no qualified frame lift points, hoist attachment, jack pick-up or lift-height path.',
  'Pin withdrawal: both wishbones lack positive support fixtures; spring/coilover control and pin retainers unresolved.',
  'Detached corner transport: stationary cradle has no casters, lifting lugs or approved lifting fixture.',
  'Arm-only full-corner manipulation: known original hardware already exceeds one UR20 payload; total module mass/CG unknown.',
  'Rear fixed-arm service: base X0.9 to rear station X−1.35 gives 2.25 m longitudinal separation, exceeding1.75 m nominal reach.',
  'Operation at any support load: no safe working load, structural analysis, load sharing/stability/floor approval or proof test.'
 ],
 'display_rules':['Show as separate optional original development fixtures.','Label no assigned load rating and no lifting function in fixture mode.','Do not place proprietary gantry/stand/hoist meshes or infer OEM geometry.','Do not animate unsupported lifting, pin withdrawal, automatic fixture placement or loaded translation.','Do not call C02 q=0 support pose a qualified maintenance state.','Do not carry C02 two-pin boundary into steering revisions without revising links.'],
 'private_source_policy':'Only original fixture solids are exported. No OEM drive STEP/PDF, extracted proprietary meshes, user photographs, credentials or OEM fixture details are included.',
 'qualification_gates':['Fixture handling/positioning method: trestles and cradle exceed UR20 payload','Measured full vehicle and corner mass/CG','All intermediate support reactions and stability','Rail wall local bearing/crushing/buckling','Trestle/cradle stress,buckling,welds,fatigue and proof load','Material/plate stock and corrosion choices','Qualified floor/slab/anchors','Liner attachment/contact/tire condition','Locator screw threads/preload/retention','Capture bolt grade/engagement/torque and moment capacity','Selected lift gear and designated load-bearing lifting points','Actual suspension droop and insertion/extraction swept volume','Wishbone props and spring energy control','Connectors,brake isolation and pin retention']
}
(P/'service_interface_contract_S01.json').write_text(json.dumps(contract,indent=2))
sources={'checked_date':'2026-10-09','source_geometry_included':False,'official_sources':[
 {'title':'ESCO 10498-PAIR manufacturer product page','url':'https://esco.net/product/3-ton-performance-jack-stand-pair/','use':'335–546 mm height; manufacturer rated stand only, not fixture rating.'},
 {'title':'ESCO 10497/10498/10499 operating instructions, April2025','url':'https://esco.net/wp-content/uploads/2025/05/10497_10498_10498_Instructions-04.25.A.pdf','use':'Center load; hard level floor; no added material for height; manufacturer-supplied attachments only; no unapproved modifications.'},
 {'title':'US Jack garage stand specification sheet2023','url':'https://www.usjack.com/wp-content/uploads/Garage-Stands-23.pdf','use':'Taller candidate range and per-pair ratings only; dimensions vary against older manual, ordered version must be checked.'},
 {'title':'US Jack garage stand manual2021','url':'https://www.usjack.com/wp-content/uploads/GARAGE-STANDS-2021-1.pdf','use':'Matched pair at one vehicle end only; simultaneous support of both ends prohibited; not used in S01.'},
 {'title':'Vestil AHA aluminum gantry','url':'https://www.vestil.com/product.php?FID=522','use':'Separate procurement candidate only; no gantry model or capacity transfer.'},
 {'title':'Vestil AHA manual','url':'https://vestildocs.com/manuals/AHA,%20MANUAL.pdf','use':'Parent-sourced restrictions; full lift/rigging compatibility unresolved.'},
 {'title':'Harrington electric chain hoist catalog','url':'https://www.harringtonhoists.com/download/2021/02/09/1ftfuxzghb_Electric_Chain_Hoist_Catalog.pdf','use':'Parent-sourced candidate NERP020C; no source CAD or lifting interface copied.'}
 ],'original_geometry_references':['R07 frame verification and STEP','C02_R05 interface contract, original R04 upright and R02 wheel adapter STEP geometry','C01 original wheel contract/STEP','R01 original body STEP'],'not_read':['private OEM drive STEP','private OEM drive PDF','user photographs']}
(P/'SOURCES.json').write_text(json.dumps(sources,indent=2))
