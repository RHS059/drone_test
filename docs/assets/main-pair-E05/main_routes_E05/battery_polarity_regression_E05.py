"""BAT548110620 drawing-to-BA02 orientation check, original numeric facts only."""
from pathlib import Path
import json,math
# Drawing right direction follows its asymmetric fitting, installed atY−52.5.
drawing_width=647.6;fitting_from_left=376.3;offset=fitting_from_left-drawing_width/2
assert math.isclose(offset,52.5,abs_tol=1e-9)
installed_fitting_y=-52.5;right_to_C_Y=installed_fitting_y/offset;assert right_to_C_Y==-1
terminals=[]
for i,cx in enumerate([-975,-625],1):
 for role,draw_x in [('positive',-275.25),('negative',275.25)]:
  p=[cx-54.05,right_to_C_Y*draw_x,169.6];terminals.append({'id':f'BAT{i}:'+('+'if role=='positive'else'-'),'role':role,'point_C_mm':p,'source_polarity_verified':True,'source_terminal_contact_height_revision_confirmed':False})
assert all(t['point_C_mm'][1]>0 if t['role']=='positive'else t['point_C_mm'][1]<0 for t in terminals)
out={'revision':'E05','source':'https://www.victronenergy.com/upload/documents/LiFePO4-Battery-51.2V100Ah-NG.pdf','source_pdf_SHA256':'d153636d0bb1cb84ea4c3c339746618c97fd02859398404febbc8a92a2a27d4b','drawing_labels':{'left':'positive','right':'negative'},'drawing_fitting_offset_toward_right_mm':offset,'installed_fitting_Y_mm':installed_fitting_y,'drawing_right_to_vehicle_Y_sign':right_to_C_Y,'terminals':terminals,'passes':True,'correction':'Earlier BA02 assumed node names reversed polarity; use this verified function mapping, never those names alone. Physical max-case geometry unchanged.','height_gate':'Installed169.6 comes from sourceSTEP upper conducting annulus and BA02bottom−69; discrepancy with234.7drawing total height remains supplier revision gate.'}
Path(__file__).with_name('battery_polarity_regression_E05.json').write_text(json.dumps(out,indent=2)+'\n');print('battery orientation assertions passed')
