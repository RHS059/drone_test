"""Original adapter R04: preferred Ø15 M8 counterbores. R03 preserved. Not fabrication release."""
from generate_cad import *
def adapter():
    # Exact nominal envelopes, proposed machining features. No proprietary coupling geometry.
    s=cq.Workplane('XY').circle(50).extrude(23.5)
    s=s.union(cq.Workplane('XY').circle(25).extrude(-2.5))
    # Nonlocating design relief for confirmed vendor annular skirt (R31.5..37.5 x3).
    s=s.cut(cq.Workplane('XY').circle(38).circle(31).extrude(3.5).translate((0,0,20)))
    for a in range(0,360,60):
        x,y=40*math.cos(math.radians(a)),40*math.sin(math.radians(a))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(4.25).extrude(25))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(7.5).extrude(12).translate((0,0,11.5)))
    for a in range(45,405,90):
        x,y=25*math.cos(math.radians(a)),25*math.sin(math.radians(a))
        s=s.cut(cq.Workplane('XY').center(x,y).circle(2.5).extrude(12).translate((0,0,11.5)))
    # Index pin seats intentionally deferred until checked manufacturer orientation is resolved.
    r=export([('original_adapter_nominal_R04',s.val())],'adapter_R04')
    r.update(manufacturer_max_M8_protrusion_mm=7,manufacturer_M8_torque_Nm=16,manufacturer_M8_class='8.8 ISO4762',nominal_max_M8_length_before_tolerances_mm=18.5,outer_counterbore_ligament_mm=2.5,nominal_total_thickness_mm=26,face_separation_mm=23.5,ur_pilot_protrusion_mm=2.5,ur_pilot_diameter_mm=50,pilot_fit_status='Nominal geometry only; male fit/tolerance NOT selected or approved',M8_clearance_count=6,M8_clearance_diameter_mm=8.5,M8_counterbore_diameter_mm=15,M8_counterbore_depth_mm=12,M6_tap_pilot_count=4,M6_tap_pilot_diameter_mm=5,M6_tap_pilot_depth_mm=12,locating_pin_seats='not modeled pending validated datum/index requirements',thread_representation='tap-drill holes only, threads not cut',release_blockers=['Pilot fit unapproved','Thread effective engagement and drill tip relief unresolved','Index pin orientation/seats unresolved','Screw grade,length,head tooling clearance and torque unresolved','Adapter strength and payload/inertia limit review unresolved','Full vendor assembly swept-volume check pending'])
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
    (P/'adapter_R04_verification.json').write_text(json.dumps(r,indent=2))
    print('ADAPTER',r['assembly_properties'],flush=True)
    return r

if __name__=='__main__':adapter()
