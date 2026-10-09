from pathlib import Path
import cadquery as cq,json,numpy as np
P=Path(__file__).parent
body=cq.importers.importStep(str(P/'body_power_R01.step')).val()
# These remain envelopes provided by the suspension worker, not acquired qualified assemblies.
rows=[]
for x in [-1350,0,1350]:
 for sy in [-1,1]:
  sh=cq.Workplane('XY').box(120,280,630).translate((x,sy*660,-115)).val()
  v=body.intersect(sh).Volume();rows.append({'station_m':[x/1000,sy*.94,-.25],'reservation_bounds_m':[[x/1000-.06,min(sy*.52,sy*.80),-.43],[x/1000+.06,max(sy*.52,sy*.80),.20]],'body_intersection_mm3':v,'minimum_body_distance_m':body.distance(sh)/1000})
well=cq.Workplane('XY').box(650,720,417).translate((25,0,128.5)).val()
frame=cq.importers.importStep(str(P/'reference_frame_R06.step')).val()
opt={'status':'unmodeled structural variant; not extra installed capacity','proposed_well_bounds_m':[[-.3,-.36,-.08],[.35,.36,.337]],'R06_frame_intersection_mm3':well.intersect(frame).Volume(),'R06_frame_minimum_clearance_m':well.distance(frame)/1000,'present_tool_bay_clear_height_mm':234,'battery_height_mm':276,'required_changes':['Replace/cut existing tool-bay base deck; current battery envelope would intersect it','New recessed welded well, access lid support and qualified retention','Removal of this low tool/payload volume','Recheck revised frame, station-centred suspension clamps and cable route','Electrical bank, inrush, bus/current sharing and fusing qualification remain necessary'],'nominal_four_unit_mass_kg':62.4,'nominal_four_unit_energy_Wh':6144,'do_not_infer':['more batteries guarantee power compatibility','sum of ratings is a qualified pack rating','current tool bay already fits batteries']}
rep={'status':'provisional nominal packaging check only','suspension_reservations':rows,'minimum_clearance_m':min(x['minimum_body_distance_m'] for x in rows),'suspension_full_geometry_checked':False,'suspension_motion_sweep_performed':False,'optional_second_bay':opt}
(P/'reservation_checks.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
