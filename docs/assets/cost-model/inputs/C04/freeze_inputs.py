#!/usr/bin/env python3
"""Copy selected factual JSON ledgers only; never vendor CAD or fetched documents."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/shared/ugv-rover-integration')
MECH=Path('/workspace/shared/ugv-reconstruction/mechanical/connection_completion_C04')
INPUTS={
'historical_C03_model.json':ROOT/'cost-model/cost_model.json',
'historical_C03_sources.json':ROOT/'cost-model/sources.json',
'wheel_price_observations.json':ROOT/'cost-model/C04-source-observations/wheel-price-observations.json',
'victron_price_observations.json':ROOT/'cost-model/C04-source-observations/victron-price-observations.json',
'mechanical_mass_BOM_C04_R01.json':MECH/'mechanical_mass_BOM_C04_R01.json',
'PUBLIC_SOURCE_FREEZE_C04_R02.json':MECH/'PUBLIC_SOURCE_FREEZE_C04_R02.json',
'structural_connections_C04_R05_manifest.json':MECH/'structural_connections_C04_R05_manifest.json',
'body_R01_verification.json':ROOT/'body-power/verification.json',
'body_PR01_manifest.json':ROOT/'body-power/panel-retention/replacement_addition_manifest.json',
'body_PR01_check.json':ROOT/'body-power/panel-retention/retention_check.json',
'body_SO02_E04P_selected.json':ROOT/'body-power/shock-opening-study/SELECTED_PACKAGE.json',
'body_SO02_E04P_parts.json':ROOT/'body-power/shock-opening-study/partition_trough_check_SO02_E04P.json',
'body_PR01_material_source.py':ROOT/'body-power/panel-retention/build_panel_retention.py',
'wheel_candidates.json':ROOT/'wheel-drive-hardware/candidate-Jantsa16p5-Trelleborg-R01.json',
'actuator_contract_R02.json':ROOT/'steering-actuator/actuator_interface_contract_R02.json',
'wheel_nut_contract.json':MECH/'drive/direct_wheel_nut_contract_C04_R01.json',
'electrical_mass_ledger.json':ROOT/'electrical-drive/freeze_E04/original_mass_ledger_E04.json',
'battery_strap_source.json':ROOT/'battery-alternative/BA02/strap_source_and_cost_record.json',
'battery_original_hardware_mass.csv':ROOT/'battery-alternative/BA02/original_hardware_mass.csv',
'electrical_bom_E04.json':ROOT/'electrical-drive/freeze_E04/bom_E04.json',
'electrical_contract_E04.json':ROOT/'electrical-drive/freeze_E04/electrical_connection_contract_E04.json',
'electrical_topology_E04.json':ROOT/'electrical-drive/freeze_E04/electrical_topology_E04.json',
'electrical_temperature_limits.json':ROOT/'electrical-drive/victron_candidate/temperature_limit_tests.json',
'electrical_trough_contract.json':ROOT/'electrical-drive/victron_candidate/switchgear_E04/rear_trough_patch_contract.json',
'battery_BA02_manifest.json':ROOT/'battery-alternative/BA02/replacement_addition_manifest.json',
'battery_BA02_verification.json':ROOT/'battery-alternative/BA02/verification.json',
}
def main():
 rows=[]
 for name,p in INPUTS.items():
  data=p.read_bytes();(HERE/'inputs'/name).write_bytes(data)
  rows.append(dict(file='inputs/'+name,source=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 (HERE/'input-manifest.json').write_text(json.dumps({'selection':'C04 structure R05; PR01 + SO02_E04P + E04 + BA02', 'inputs':rows},indent=2)+'\n')
 print('Frozen',len(rows),'input records')
if __name__=='__main__':main()
