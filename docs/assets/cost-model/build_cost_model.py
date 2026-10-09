#!/usr/bin/env python3
"""Build the C02_R06 cost reference model. Public observations, never quotations."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, re

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
APP=HERE.parents[2]
OBSERVED='2026-10-09'
REV='C02_R06'
LEDGER=BASE/'corners'/f'mass_cost_ledger_{REV}.json'
SNAPSHOT=APP/'docs/assets/mechanical/mass-power-snapshot.json'
BODY=BASE/'body-power/verification.json'
CONTRACT=LEDGER.with_name(f'interface_contract_{REV}.json')
source_rows=[]

def source(id,url,publisher,kind,facts,**kw):
    row=dict(id=id,url=url,publisher=publisher,kind=kind,retrieved_on=OBSERVED,
             retrieval=kw.pop('retrieval','Public web page text; may be search-provider cached. No checkout or vendor confirmation.'),facts=facts,**kw)
    source_rows.append(row)
    return id

source('tire_price','https://www.vividracing.com/bfgoodrich-mudterrain-km3-35x1250r18-p-152504463.html','Vivid Racing','supplier_own_public_listing',
       'MSPN72204,35x12.50R18 KM3 is listed at486.99USD per tire; page indicates stock and a10USD promotional ground-shipping amount. Six-unit destination freight,tax and stock are unconfirmed.',
       price=486.99,currency='USD',sku='72204',seller_region='United States',tax_basis='not established',shipping_basis='10USD promotional page amount; quantity/destination applicability unknown, not included',availability='Page says in stock; six-unit allocation not verified',condition='standard retail listing; no used/refurbished condition indicated',exact_sku_match=True)
source('tire_alternate_price','https://ntwonline.com/35x12-50r18e-blk-mud-terrain-km3-bfgoodrich-tires/','National Tire & Wheel','supplier_own_public_listing',
       'Same72204 tire lists491.99USD. Page also contains zero-valued set placeholders; these are not free prices and are not used. Freight and taxes unconfirmed.',
       price=491.99,currency='USD',sku='BFKM3 72204',seller_region='United States',exact_sku_match=True)
source('tire_specs','https://www.usautoforce.com/wp-content/uploads/2025/03/BFGoodrich_PCLT_Databook.pdf.pdf','BFGoodrich databook hosted by U.S. AutoForce','manufacturer_documentation',
       'Printed page27,MSPN72204:35x12.50R18/E123Q;34.5in(876.3mm)diameter measured on10in rim; approved rim width8.5–11in. Actual size on selected8.5in rim is unverified.',page_printed=27,not_price=True)
source('rim_price','https://shop.evocorse.com/en/catalog/catalog_item/dakarzero-85x18-se5240060141.aspx?k=cm0752170010-5','EVO Corse','manufacturer_own_public_listing',
       'Rendered bundle SE5240060141+CM0750180040-5 lists481.89EUR VAT included:18x8.5,5x165.1,ET18,114.1mm bore. Opened text says zero stock; search index says two available in15days. Current stock is unresolved. The URL query kit differs from rendered kit.',
       price=481.89,currency='EUR',sku='SE5240060141 + CM0750180040-5',seller_region='Italy',tax_basis='VAT included; rate and destination treatment unconfirmed',shipping_basis='not established',availability='conflicting cached stock statements; unconfirmed',exact_sku_match=True)
source('wheel_nuts','https://evocorse.com/en/product/end-nut-lug-for-land-rover-m16x1-5-black-zinc-plated/','EVO Corse','manufacturer_documentation',
       'CM0750180040 flat-seat M16x1.5 nut with washer; catalogue mass212g. Thirty nuts are covered by six rendered five-nut rim bundles; do not add independent nut prices to that bundle.',not_price=True)
source('battery_price','https://www.westmarine.com/relion-48v030-gc2-lithium-iron-phosphate-deep-cycle-battery-48v-30ah-20659967.html','West Marine','supplier_own_public_listing',
       'Manufacturer SKU48V030-GC2,retailer20659967:1349.99USD each. Product page says out of stock. This is the non-LT candidate; destination tax,freight and eligible post-recall serials remain unconfirmed.',
       price=1349.99,currency='USD',sku='48V030-GC2',seller_sku='20659967',seller_region='United States',tax_basis='not established',shipping_basis='not established',availability='out of stock in retrieved product page',condition='standard retail listing; no used/refurbished condition indicated',exact_sku_match=True)
source('battery_specs','https://www.relionbattery.com/products/lithium/insight-gc2-48v','RELiON','manufacturer_documentation',
       'Per module:51.2V,30Ah,1536Wh,15.6kg;45A recommended and100A maximum continuous discharge; parallel allowed up to10,series prohibited. Catalogue cycle-life claims are not rover mission validation.',not_price=True)
source('battery_recall','https://www.relionbattery.com/product-recall-us','RELiON','manufacturer_safety_recall',
       'Certain48V030-GC2 serial ranges are recalled for overheating/fire risk. U.S. remedy is repair. Manufacturer instructs affected owners to stop use and coordinate return. No serials or purchases exist in the evidence for this candidate BOM.',
       affected_model='48V030-GC2',affected_serial_ranges=[['RB48300020210314057','RB48300020210314729'],['RB48300020210330001','RB48300020210330715'],['RB48300020210507012','RB48300020221016550']],region='United States')
source('ur20_quote','https://www.universal-robots.com/products/ur20-1750/','Universal Robots','manufacturer_quote_required',
       'Manufacturer product page requests pricing and lists64kg arm weight. No exact arm-only commercial SKU,software/controller bundle or usable public arm-only price was established; legacy UR20 CAD is not automatically a new product revision.',price=None,currency=None)
source('ur20_bundles','https://automationdistribution.com/universal-robots-ur20-collaborative-robot/','Automation Distribution','supplier_configuration_documentation',
       'UR20 commercial packages can include OEM DC control boxes,e.g.200129(PolyScope5)and200170/200376(PolyScopeX). Do not add a separate controller price if quoting a controller-inclusive arm package.',not_price=True)
source('oem_dc_specs','https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod_oem_cb_all/oem_cb_all_specs_root.htm','Universal Robots','manufacturer_documentation',
       'OEM DC envelope451x150x168mm,mass4.3kg,input19–72V with24–48V typical; maximum inrush400A. Two-dimensional reservations do not settle exact controller revision or arm compatibility.',not_price=True)
source('oem_dc_candidate_price','https://automationdistribution.com/universal-robots-controller-box-oem-dc-cb5-5/','Automation Distribution','supplier_own_public_listing',
       'Standalone CB5.5 OEM DC controller SKU200143 lists8217USD,new,factory stock,tariff surcharge included. Exact baseline controller revision remains unselected; tax,freight and any arm-package inclusion are unresolved.',price=8217,currency='USD',sku='200143',seller_region='United States',tax_basis='tariff surcharge included; sales tax not established',shipping_basis='not established',availability='factory stock per page; allocation unverified',exact_sku_match=False)
source('gripper_price','https://www.logic-control.com/robotiq-agc-grp-2f85','Logic, Inc.','supplier_own_public_listing',
       'AGC-GRP-2F85 basic gripper lists5205USD each; lead time requires confirmation. Seller lists fingertips,locking pins and screw kit; manufacturer ordering descriptions differ on fingertip inclusion,so confirm package contents. No coupling is included in this price.',
       price=5205,currency='USD',sku='AGC-GRP-2F85',seller_region='United States',tax_basis='not established',shipping_basis='not established',availability='contact for lead time; no contact made',condition='standard distributor listing; no used/refurbished condition indicated',currency_basis='US seller dollar price; no destination checkout',exact_sku_match=True)
source('coupling_price','https://www.kingbarcode.com/GRP-CPL-062','King Barcode','supplier_own_public_listing',
       'Exact modeled GRP-CPL-062 controller-connected coupling lists644USD each,quantity1 standard price. Backorder and pricing confirmation are requested on the page. External cable and controller/RS485 interface are not priced by this listing.',
       price=644,currency='USD',sku='GRP-CPL-062',seller_region='United States (Henderson,Nevada)',tax_basis='not established',shipping_basis='not established',availability='backorder; price and lead time need supplier confirmation',condition='standard distributor listing; no used/refurbished condition indicated',currency_basis='US seller dollar price; no destination checkout',exact_sku_match=True)
source('coupling_routes','https://robotiq.zendesk.com/hc/en-us/articles/360060115033-Couplings-and-cables-UR','Robotiq','manufacturer_documentation',
       'GRP-CPL-062 is the controller-connected coupling. GRP-ES-CPL-062 is a different wrist-connected coupling; these part numbers must not be conflated.',not_price=True)
source('coupling_wrist_gate','https://blog.robotiq.com/knowledge/how-to-identify-the-type-of-connector-at-the-flange-of-universal-robots-e-series-robot-5-1736280763712','Robotiq','manufacturer_documentation',
       'Updated2026-09-21:UR20 has a female wrist connector. For direct wrist connection Robotiq lists GRP-ES-CPL-077 and CBL-COM-2077-01. Both e-Series coupling routes list ISO50-4-M6; matching bolt pattern does not prove identical body geometry. No baseline mesh substitution is authorized by this finding.',source_updated_on='2026-09-21',not_price=True)
source('coupling_external_route','https://blog.robotiq.com/knowledge/longer-e-series-cable','Robotiq','manufacturer_documentation',
       'Robotiq supports a CB-series coupling with10m external cable as an alternative to unsupported wrist-cable extensions. This is source support for a route,not completed integration of the present rover.',not_price=True)
source('coupling_alt_price','https://www.logic-control.com/robotiq-grp-es-cpl-077','Logic, Inc.','supplier_own_public_listing',
       'GRP-ES-CPL-077 lists680USD; kit includes mechanical coupling,screws,CBL-COM-2077-01 cable and protector. Alternative wrist-connected route only; not an addition to current GRP-CPL-062 baseline.',price=680,currency='USD',sku='GRP-ES-CPL-077',seller_region='United States',tax_basis='not established',shipping_basis='not established',availability='contact for lead time',exact_sku_match=False)
source('ur20_adapter_gate','https://blog.robotiq.com/knowledge/plug-and-play-on-ur20-5-1736280730313','Robotiq','manufacturer_documentation',
       'Robotiq states UR supplies an adapter converting the UR20 flange to50mmPCD/4xM6. If missing,ACC-APL-UR20 is a replacement option. The present original adapter_R04 is a different,unqualified fabrication design; do not double-count a replacement plate as baseline.',not_price=True)
source('adapter_alt_price','https://automationdistribution.com/robotiq-acc-apl-ur20/','Automation Distribution','supplier_own_public_listing',
       'ACC-APL-UR20 plate kit lists667.97USD. Replacement/reference alternative only; do not add to original adapter_R04 or assume omission from purchased UR packages.',price=667.97,currency='USD',sku='ACC-APL-UR20',seller_region='United States',tax_basis='not established',shipping_basis='not established',availability='contact for availability and lead time',exact_sku_match=False)
source('drive_reference','https://www.e-comer.com/en/?Itemid=461','e-comer/Benevelli','manufacturer_reference_from_existing_source_ledger',
       'Exact WD220-SMAC132-050-48V-EMB-5STUDS candidate price and mass remain unknown. Existing source ledger records2.2kW,S2-60min,47A motor rating; not verified DC-bus current. This page could not be opened during this cost refresh. Restricted supplier geometry is not redistributed.',price=None,currency=None,retrieval='Existing source ledger and rating evidence; public-page refresh unavailable')
source('drive_rejected_price','https://evshop.it/en/products/motor-wheel-wd220-48v-3kw','EVSHOP/EVSAFE','supplier_own_public_listing_nonmatching_variant',
       '2499EUR WD220 listing is3.0kW S2-60min and a4-bolt BMW flange. It is not the2.2kW5-stud baseline. Price is deliberately rejected as a substitute;16-week estimated delivery appears on the page.',price=2499,currency='EUR',sku='WD220-48V 3.0kW four-bolt variant',seller_region='Italy',tax_basis='not established',shipping_basis='calculated at checkout',availability='estimated16weeks',exact_sku_match=False)
source('aux_research','https://www.victronenergy.com/media/pricelist/Pricelist_Victron_EUR_C_2026-Q2_web.pdf','Victron Energy','existing_manufacturer_reference_research_only',
       'Orion-Tr48/12-30 is an unselected research candidate from the existing body-power ledger. No quantity,cost or electrical compatibility is accepted into baseline.',not_price=True,retrieval='Existing body-power source ledger; not a new price observation')

# Supplied, version-pinned mechanical evidence is read; no source CAD is changed.
ledger=json.loads(LEDGER.read_text())
snapshot=json.loads(SNAPSHOT.read_text())
body=json.loads(BODY.read_text())
assert any(abs(snapshot['mass_known_subset_kg']-x)<1e-8 for x in [976.3621302801703,976.3493556219631]), 'Mass snapshot changed beyond approved R05/R06 reconciliation; review before updating.'

parts=[]
def part(id,name,sku,qty,kind='purchased_part',selection='baseline_candidate',essential=True,price=None,currency=None,price_source=None,mass=None,mass_snapshot=False,notes='',scope='vehicle',included_in=None,sources=(),**extra):
    p=dict(id=id,name=name,sku=sku,quantity=qty,quantity_unit='each',scope=scope,supply_kind=kind,selection_status=selection,
      acquisition_status='no_purchase_or_owned_hardware_evidence',essential=essential,unit_price=price,currency=currency,
      extended_price=(float(Decimal(str(price))*Decimal(str(qty))) if price is not None and qty is not None else None),
      pricing_status=('public_reference_not_quote' if price is not None else ('included_in_bundle_no_separate_allocation' if included_in else 'unpriced')),
      price_source_id=price_source,included_in_cost_of=included_in,unit_mass_kg=mass,
      mass_basis=('source_snapshot_or_catalogue_not_weighed' if mass is not None else 'unknown'),
      included_in_pinned_mass_subtotal=mass_snapshot,source_ids=list(sources),notes=notes,**extra)
    parts.append(p)
    return p

part('frame_R07','Original welded frame R07','original:frame_R07',1,'original_fabrication',selection='modeled_original_development',mass=386.9529671773959,mass_snapshot=True,notes='Quote required:stock,welds,post-weld machining,finishing,inspection and scrap. Geometry is not fabrication released.')
part('body_R01','Original body,trays,restraints and modeled hardware R01','original:body_power_R01',1,'original_fabrication',selection='modeled_original_development',mass=body['body_hardware_mass_kg'],mass_snapshot=True,notes='175 original CAD parts aggregated; quote against original_cutlist.csv. Excludes four batteries and two controllers,which are separate rows. Material densities assumed.')
part('adapter_R04','Original tool-flange adapter R04','original:adapter_R04',2,'original_fabrication',selection='modeled_original_development',mass=1.316846623,mass_snapshot=True,notes='Unqualified original adapter; mandatory Robotiq coupling remains separately purchased. Do not add alternative ACC-APL-UR20 plate on top.')
for item in ledger['items']:
    reference=item['mass_kg_per_corner'] is None
    part(item['part'],item['part'].replace('_',' '),'original:'+item['part'],item['qty_rover'],
        kind='reference_geometry' if reference else 'original_fabrication',selection='reference_envelope' if reference else 'modeled_original_development',
        essential=not reference,mass=item['mass_kg_per_corner'],mass_snapshot=not reference,scope='reference_only' if reference else 'vehicle',
        notes='Bearing fit envelope only;not an extra purchased bearing. Production bearing row separately records provisional72units.' if reference else 'C02_R06 nominal volume times assumed density. Material,machining,finish,inspection,quantity-break and fastening specification require fabrication quote.',
        source_step_sha256=item['sha256_STEP'])
part('tires','BFGoodrich Mud-Terrain T/A KM3 35x12.50R18/E123Q','72204',6,price=486.99,currency='USD',price_source='tire_price',sources=['tire_price','tire_specs'],notes='Exact size/SKU reference;not OEM CAD.876.3mm catalog diameter on10in measuring rim;actual size on8.5in rim unverified. Mount/balance,valves,tax and six-tire freight unpriced.')
part('rims','EVO Corse DakarZero 18x8.5 ET18 + required five-nut road kit','SE5240060141 + CM0750180040-5',6,price=481.89,currency='EUR',price_source='rim_price',sources=['rim_price'],notes='5x165.1,CB114.1,flat-seat. Price includes VAT and five-nut kit each. Stock and destination tax/freight unresolved. Rim mass remains unknown;undocumented raw page fields are not accepted as mass evidence.')
part('wheel_nuts','EVO flat-seat M16x1.5 nuts','CM0750180040',30,included_in='rims',mass=0.212,sources=['wheel_nuts','rim_price'],notes='Thirty nuts included in six priced rim bundles;no independently allocated unit cost.6.36kg is published additional mass outside the pinned976.36kg snapshot. Stud thread/engagement remain unqualified.')
part('drives','e-comer WD220 drive with EM brake and5studs','WD220-SMAC132-050-48V-EMB-5STUDS',6,sources=['drive_reference'],notes='2.2kW S2-60min,not continuous.47A is a motor rating,not verifiedDC-bus input. Exact mass and price unknown;do not use four-bolt3kW price.')
part('batteries','RELiON InSight non-LT battery','48V030-GC2',4,price=1349.99,currency='USD',price_source='battery_price',mass=15.6,mass_snapshot=True,sources=['battery_price','battery_specs','battery_recall'],notes='Proposed parallel bank:6.144kWh nominal. Price listing is out of stock. Serial-specific recall clearance required before purchase/use;no battery serials are known. Not the-LT model.')
part('arms','Universal Robots UR20 arm','UR20 exact arm-only ordering SKU unresolved',2,mass=64,mass_snapshot=True,sources=['ur20_quote','ur20_bundles'],notes='Purchased-part requirement with unknown price;no evidence of an actual purchase. Exact revision,software,cables,pendant and OEMDC package scope require quote. Controller-inclusive package must replace,not duplicate,the two controller rows.')
part('arm_controllers','Universal Robots OEM DC controller','exact CB revision unresolved',2,mass=4.3,mass_snapshot=True,sources=['oem_dc_specs','oem_dc_candidate_price','ur20_bundles'],notes='Two dimensional reservations.200143CB5.5 price is shown only as a separate candidate reference because controller revision and package inclusion are unresolved.')
part('grippers','Robotiq2F-85 basic gripper','AGC-GRP-2F85',2,price=5205,currency='USD',price_source='gripper_price',sources=['gripper_price'],notes='Manufacturer source ordering text and seller disagree on fingertip inclusion;confirm exact kit. Coupling,cable/interface and any additional fingertips are separately tracked. No gripper mass accepted into pinned subtotal.')
part('couplings','Robotiq controller-connected coupling (current CAD reference)','GRP-CPL-062',2,price=644,currency='USD',price_source='coupling_price',sources=['coupling_price','coupling_routes','coupling_external_route'],notes='Separate purchased electronics-containing coupling;original adapter cannot replace it. GRP-ES-CPL-062 and GRP-ES-CPL-077 are different SKUs. Current visual mesh remains a licensed reference;electrical route and exact cable/interface unresolved.')
part('gripper_cable_interface','Gripper device cables,RS485/controller interface and required integration hardware',None,None,selection='required_unresolved',notes='Two grippers require validated power/communications. Counts and exact cable/USB/interface SKUs remain unknown;do not assume bare coupling price includes full route.',sources=['coupling_external_route','coupling_routes'])
part('gripper_fingertips','Any additional approved gripper fingertips',None,None,selection='required_scope_unresolved',notes='Whether separately needed depends on confirmed AGC-GRP-2F85 package contents and task. Do not count included fingertips twice.',sources=['gripper_price'])
part('spherical_bearings','Provisional suspension spherical bearings','GE20ES candidate specification,manufacturer unresolved',72,selection='research_candidate',notes='72 is the C02_R06 provisional count,not a qualified supplier selection. Bearing-envelope rows are references and do not add another quantity.')
part('coilovers','Coilover,spring and damper assemblies',None,6,selection='required_unresolved',notes='No approved rate,damping,stroke,load or supplier selection;mass/price unknown.')
for id,name,qty,note in [
 ('suspension_fasteners','Missing suspension pins,bearing retainers,bolts and locking hardware',None,'Excludes nominal original hardware already present in corner rows;exact purchased schedule unresolved.'),
 ('wheel_studs','Wheel output studs and retained input hardware',None,'Exact thread,length,grade,seat and engagement must be finalized.'),
 ('traction_inverters','Traction inverters/controllers and tuning',None,'Six motors do not prove six inverter packages;architecture and quantity unresolved.'),
 ('power_distribution','Harness,busbars,fuses,contactors,precharge and electrical protection',None,'Current-sharing,module-dropout,inrush and regeneration remain unqualified.'),
 ('charger','Qualified battery charger and charging connections',None,'Exact output,grid connection and charging workflow unresolved.'),
 ('aux_converter','Selected auxiliary DC/DC conversion',None,'Victron research alternative is not an approved baseline selection.'),
 ('cooling','Cooling and thermal-management hardware',None,'Two UR20 controller reservations do not establish complete cooling cost.'),
 ('safety_controls','Safety control,e-stop,sensors,compute and communication hardware',None,'No complete safe operational controller/sensor BOM.'),
 ('tire_services','Valve,mounting,balancing and tire-service work',None,'Not included in bare tire listing or inferred from rim mounting-nut kit.'),
 ('steering','Steering or validated skid-steer solution',None,'No implemented steering mechanism in current CAD;required capability not costed as zero.'),
 ('task_tools','Required task-specific tools and fixtures',None,'No autonomous repair/replication process demonstrated;tools,payload and offboard fixtures separately quoted.'),
 ]:
    part(id,name,None,qty,selection='required_unresolved',notes=note)
for id,name in [('build_labor','Direct assembly,wiring,commissioning and rework labor'),('engineering_nre','Engineering,software,integration and safety qualification'),('logistics_tax','Destination taxes,duties,freight and procurement'),('external_workcell','Offboard lifting,service fixtures and workcell')]:
    part(id,name,None,None,kind='service_or_cost_category',selection='required_unresolved',scope='external_workcell' if id=='external_workcell' else 'build_cost',notes='No current work breakdown or quote. Costs embedded in supplier fabrication quotes must not be added again as direct labor.')

alternatives=[
 dict(id='oem_dc_200143',replaces_id='arm_controllers',sku='200143',quantity_if_selected=2,unit_price=8217,currency='USD',source_id='oem_dc_candidate_price',status='unselected_controller_revision',baseline_included=False),
 dict(id='wrist_coupling_077',replaces_id='couplings',sku='GRP-ES-CPL-077',quantity_if_selected=2,unit_price=680,currency='USD',source_id='coupling_alt_price',status='alternative_electrical_route_requires_geometry_and_wiring_review',baseline_included=False),
 dict(id='purchased_ur20_adapter',replaces_id='adapter_R04',sku='ACC-APL-UR20',quantity_if_selected=2,unit_price=667.97,currency='USD',source_id='adapter_alt_price',status='alternative_plate_may_already_be_in_arm_package',baseline_included=False),
 dict(id='aux_victron',replaces_id='aux_converter',sku='Orion-Tr48/12-30',quantity_if_selected=None,unit_price=None,currency=None,source_id='aux_research',status='research_only',baseline_included=False),
]

# Currency groups are reference baskets, not a combined landed total.
baskets=[]
for currency in sorted({p['currency'] for p in parts if p['unit_price'] is not None}):
    chosen=[p for p in parts if p['currency']==currency and p['unit_price'] is not None]
    baskets.append(dict(currency=currency,reference_subtotal=float(sum((Decimal(str(p['extended_price'])) for p in chosen),Decimal(0))),
       line_ids=[p['id'] for p in chosen],line_count=len(chosen),complete_build_total=False,
       tax_basis='VAT included in rim listing only' if currency=='EUR' else 'destination sales tax not established',shipping_total=None))

actual_inputs={
 'currency':None,'site_tariff_per_kwh':None,'measured_grid_kwh_per_operating_hour':None,
 'measured_battery_kwh_per_operating_hour':None,'charge_efficiency':None,'parked_grid_kwh_per_year':None,
 'annual_operating_hours':None,'supervision_hours_per_operating_hour':None,'supervisor_rate_per_hour':None,
 'maintenance_labor_hours_per_operating_hour':None,'technician_rate_per_hour':None,
 'maintenance_parts_per_year':None,'battery_installed_replacement_cost':None,'validated_cycle_life':None,
 'validated_discharge_fraction':None,'calendar_life_years':None,'insurance_per_year':None,
 'software_connectivity_per_year':None,'transport_per_year':None,'consumables_per_operating_hour':None,
 'complete_build_cost':None,'service_years':None,'residual_value':None,'nre_amortization':None}

scenarios=[]
for power in [2,4,8]:
    assumptions=dict(currency='USD',assumed_mean_battery_kw=power,assumed_charging_efficiency=0.9,
       assumed_tariff_usd_per_kwh=0.15,assumed_annual_operating_hours=1000,
       assumed_supervision_hours_per_robot_hour=1.0,assumed_supervisor_usd_per_hour=50,
       assumed_maintenance_labor_hours_per_robot_hour=0.1,assumed_technician_usd_per_hour=100,
       module_replacement_public_reference_usd=5399.96,assumed_cycle_life=2000,
       assumed_cycle_depth=0.8,assumed_calendar_life_years=5)
    energy=power/0.9*0.15
    cycle=5399.96*power/(6.144*0.8*2000)
    calendar=5399.96/(5*1000)
    reserve=max(cycle,calendar)
    outputs=dict(energy_only_usd_per_operating_hour=energy,
       assumed_supervision_usd_per_operating_hour=50,assumed_maintenance_labor_usd_per_operating_hour=10,
       battery_module_cycle_reserve_usd_per_operating_hour=cycle,battery_module_calendar_reserve_usd_per_operating_hour=calendar,
       battery_module_reserve_usd_per_operating_hour=reserve,
       modeled_partial_usd_per_operating_hour=energy+50+10+reserve,
       modeled_partial_usd_per_assumed_year=(energy+50+10+reserve)*1000,
       complete_operating_cost_usd_per_hour=None,fully_burdened_cost_usd_per_hour=None,whole_rover_runtime_hours=None)
    scenarios.append(dict(id=f'assumed_{power}kw',label=f'Illustrative {power}kW battery draw;not measured or qualified',
       inputs=assumptions,outputs=outputs,exclusions=['maintenance parts','installed battery replacement labor/freight/tax','capital recovery','NRE','consumables','insurance','software/connectivity','transport','parked energy','demand charges','downtime'],
       limits='Mean battery draw is an analyst scenario,not a mission measurement. An operating hour may span charging sessions. No continuous-drive feasibility or uninterrupted runtime is implied. Battery reserve uses public module prices only;cycle/calendar assumptions are not validated life.'))

formulas={
 'electricity_with_meter':'energy_cost_per_h = measured_grid_kWh_per_h * tariff_per_kWh',
 'electricity_without_meter_scenario':'grid_kWh_per_h = assumed_mean_battery_kW / assumed_charging_efficiency;energy_cost_per_h = grid_kWh_per_h * assumed_tariff',
 'mission_energy':'mission_grid_kWh = sum(measured_or_explicitly_assumed_segment_battery_kW * segment_hours) / charge_efficiency + parked_grid_kWh',
 'labor':'labor_per_h = supervision_h_per_robot_h * supervisor_rate + maintenance_h_per_robot_h * technician_rate',
 'battery_cycle_reserve':'module_cost * assumed_battery_kWh_per_h / (nominal_bank_kWh * assumed_cycle_depth * assumed_cycle_life)',
 'battery_calendar_reserve':'module_cost / (assumed_calendar_life_years * assumed_annual_operating_hours)',
 'battery_reserve':'max(cycle_reserve,calendar_reserve);not sum,to avoid charging twice for the same replacement mechanism',
 'parts':'maintenance_parts_per_h = annual_maintenance_parts / annual_operating_hours',
 'capital':'capital_recovery_per_h = (complete_nonbattery_installed_cost - nonbattery_residual) / (service_years * annual_operating_hours);exclude battery capital only if battery replacement reserve already amortizes it',
 'complete_opex':'energy + labor + maintenance_parts + battery_replacement + consumables + insurance + connectivity + transport + parked_energy + other_operating_costs;result=null while any required input is unknown',
 'fully_burdened':'complete_opex + capital_recovery + separately_selected_NRE_amortization;result=null while any required input is unknown',
 'price_extension':'quantity * unit_price;null if either operand unknown. Do not coerce null to zero.',
 'fx':'No automatic FX. Preserve native-currency groups until a dated exchange-rate assumption and destination are explicitly chosen.'}

local_inputs=[]
for label,path in [('mass-power-snapshot.json',SNAPSHOT),(f'mass_cost_ledger_{REV}.json',LEDGER),(f'interface_contract_{REV}.json',CONTRACT),('body-power/verification.json',BODY),('body-power/sourced_bom.csv',BASE/'body-power/sourced_bom.csv'),('wheels/SOURCES.json',BASE/'wheels/SOURCES.json'),('legacy:docs/costs.json',APP/'docs/costs.json')]:
    local_inputs.append(dict(artifact=label,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
legacy=json.loads((APP/'docs/costs.json').read_text())
model=dict(schema_version='1.0.0',title='Six-wheel UGV build and operating cost reference',as_of=OBSERVED,
 configuration=dict(corner_revision=REV,frame_revision='R07',body_revision='R01',tool_adapter_revision='R04',public_feature_commit_at_assignment='82ce94f27dd37db02015ecf62f48a54884a4a75a',not_fabrication_released=True),
 policy=dict(unknown_numeric='null,never zero',csv_null='literal null',purchased_part_meaning='Must be sourced from a supplier;does not assert purchased or owned.',public_prices='Public dated reference observations;not firm quotes or confirmed destination totals.',source_currency='Native currency kept;no FX conversion.',research_candidates='Excluded from baseline public-price baskets;never silently substitute.',bundle_accounting='Nuts included in rim bundle;controller-inclusive UR arm packages replace separate controller allowance;alternative coupling/adapter replaces baseline item.'),
 parts=parts,alternatives=alternatives,build_summary=dict(status='incomplete_essential_items_unpriced',complete_build_cost=None,currency=None,
   public_price_baskets=baskets,essential_unpriced_line_ids=[p['id'] for p in parts if p['essential'] and p['unit_price'] is None and p['included_in_cost_of'] is None],
   excluded_from_public_baskets=['all original fabrication','WD220 drives','UR20 arms','exact OEM DC controller revision','unresolved integration hardware/services','taxes except rim listing VAT','shipping','alternative/research parts'],
   new_vs_used='No used/refurbished substitution. Seller catalogue condition and eligible battery serials must be confirmed.'),
 mass_context=dict(pinned_known_subset_kg=sum(p['unit_mass_kg']*p['quantity'] for p in parts if p['included_in_pinned_mass_subtotal']),whole_vehicle_mass_kg=None,
   source_snapshot_mass_kg=snapshot['mass_known_subset_kg'],source_snapshot_corner_revision=Path(snapshot['corner_contract']).stem.replace('interface_contract_',''),
   revision_reconciliation='Approved C02_R06 replaces the six R04 uprights with R05 uprights at8.853733428185155kg each. Other included masses and attachment poses unchanged. Reconciled subtotal976.3493556219631kg; source snapshot may still be R05.',
   additional_catalog_nuts_kg=6.36,additional_catalog_nuts_in_pinned_subset=False,
   no_recomputed_complete_mass=True,warning='Pinned subtotal combines nominal CAD masses and known catalogue components. Many physical parts remain unknown. The extra nuts do not complete the mass model.'),
 electrical_context=dict(nominal_bank_kwh=6.144,battery_count=4,nominal_voltage=51.2,drive_count=6,
   drive_rating_kw_each=2.2,drive_rating_duty='S2 60min;S1 unknown',motor_current_A_each=47,DC_bus_current_basis_verified=False,
   arithmetic_recommended_battery_current_A=180,arithmetic_maximum_battery_current_A=400,system_current_rating_A=None,
   simultaneous_mechanical_rating_kw=13.2,ideal_minimum_DC_current_A_at_nominal_voltage=257.8125,
   warning='13.2kW/51.2V assumes motor mechanical output and ideal conversion,excludes arms/auxiliaries. It exceeds individually recommended battery-current sum. Neither sum is a qualified pack rating. No continuous capability or runtime established.'),
 procurement_gates=[dict(id='battery_serial_recall',severity='safety',status='unresolved_no_serials',source_id='battery_recall',message='Require traceable,unaffected or manufacturer-remedied48V030-GC2 serials. If an owned unit falls within recalled ranges,stop use and follow manufacturer remedy. No claim any candidate unit is affected.'),
   dict(id='coupling_electrical_route',severity='integration',status='unresolved',source_id='coupling_wrist_gate',message='Current GRP-CPL-062 uses controller-connected route. GRP-ES-CPL-077 is a separate wrist-connected candidate for UR20 female connector. Do not relabel current mesh or add both prices.'),
   dict(id='arm_controller_package',severity='double_counting',status='unresolved',source_id='ur20_bundles',message='Obtain exact arm/controller/cable/pendant/software scope. Count packaged controllers once.'),
   dict(id='original_manufacturing',severity='qualification',status='quote_and_release_required',source_id=None,message='Geometry validation is not manufacturing or safety release;grade,tolerances,welds,fasteners,testing and quote required.'),
   dict(id='battery_current_and_drive_duty',severity='qualification',status='unqualified',source_id='battery_specs',message='No approved mission/duty,inverter,BMS-sharing,inrush,regen,thermal or charge design.'),
   dict(id='rim_stock',severity='availability',status='unconfirmed_conflicting_cached_stock',source_id='rim_price',message='Exact old-shop listing retains price;cached stock statements conflict. Confirm current price,kit and six-unit stock before procurement.')],
 operating_cost=dict(status='actual_unknown_scenarios_only',actual_inputs=actual_inputs,actual_cost_per_operating_hour=None,whole_rover_runtime_hours=None,
   formulas=formulas,scenarios=scenarios,measurement_plan=['Log grid charging kWh and paid tariff for a representative mission,including parked energy.','Log battery DC energy,current peaks and per-module temperatures across drive,arm,idle and charging segments.','Record operator time,setup,recovery,downtime,maintenance parts and labor separately.','Obtain installed battery replacement cost and validated cycle/calendar assumptions.','Measure annual utilization before allocating fixed costs;do not divide by optimistic autonomous uptime.']),
 historical_model=dict(path='legacy docs/costs.json',version=legacy['version'],as_of=legacy['as_of'],status='historical_configuration_not_current_quote',
    old_workshop_hardware_base_usd=legacy['totals_usd']['workshop_robot_hardware']['base'],
    reasons_not_current=['Eight workshop and ten field LT batteries instead of four non-LT modules.','Different tire/drive candidates and presumed steering architecture.','Generic fabrication/arm/tool allowances,not exactSKU quotes.','Legacy runtime and hourly totals depend on that superseded architecture and must not be shown as current.']),
 evidence=dict(source_file='sources.json',bom_file='BOM.csv',local_inputs=local_inputs),
 ui_contract=dict(build_headline='Complete build cost: unknown',basket_label='Priced subset only;native currencies;not a full build quote',operating_headline='Measured operating cost: unknown',scenario_label='Assumptions-only partial operating scenario',do_not_display=['old311495.6USD as current build price','old8/10-battery runtime as current rover runtime','null as0','combinedUSD/EUR subtotal without explicitFX','S2 rating as continuous','any reference price as a completed order']))

# Keep human-facing prose readable without altering identifiers,SKUs or URLs.
prose_keys={'facts','notes','name','message','warning','limits','label','public_prices','unknown_numeric','purchased_part_meaning','research_candidates','bundle_accounting','new_vs_used','retrieval'}
replacements={
 'MSPN72204':'MSPN 72204','Model48V030':'Model 48V030','model48V030':'model 48V030','Certain48V030':'Certain 48V030',
 'SKU48V030':'SKU 48V030','retailer20659967':'retailer 20659967','SKU200143':'SKU 200143',
 'Robotiq2F-85':'Robotiq 2F-85','with5studs':'with 5 studs','with10m':'with 10 m','with24–48V':'with 24–48 V',
 'page27':'page 27','up to10':'up to 10','to50mmPCD':'to 50 mm PCD','provisional72units':'provisional 72 units',
 'two grippers':'two grippers','notDC':'not DC','not OEMDC':'not OEM DC','OEMDC':'OEM DC',
 '20143CB5.5':'20143 CB5.5','200143CB5.5':'200143 CB5.5','14USD':'14 USD',
 'zero-valued':'zero-valued','individually recommended180A':'individually recommended 180 A',
 'no10':'no 10','the2.2':'the 2.2','is3.0':'is 3.0','4-bolt':'4-bolt','million+':'million+',
 'updated2026':'updated 2026','Updated2026':'Updated 2026','subtotal976':'subtotal 976',
 'the-LT':'the -LT','as0':'as 0','old311495.6USD':'old 311495.6 USD','old8/10':'old 8/10',
}
def readable(obj):
    if isinstance(obj,list):
        return [readable(x) for x in obj]
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            if k in prose_keys and isinstance(v,str):
                for a,b in replacements.items(): v=v.replace(a,b)
                v=re.sub(r'[,;](?=\S)',lambda m:m.group(0)+' ',v)
                v=re.sub(r'(?<=\d)(USD|EUR|kWh|kW|kg|mm|weeks|days|units)(?![A-Za-z0-9])',r' \1',v)
                v=re.sub(r'(?<=[A-Za-z])(?=\d(?:\.\d+)?(?:USD|EUR|kWh|kW|kg|mm)\b)', ' ', v)
            out[k]=readable(v)
        return out
    return obj
model=readable(model)
source_rows=readable(source_rows)
parts=model['parts']
source_lookup={s['id']:s for s in source_rows}
for p in parts:
    p['quote_date']=None
    p['is_supplier_quote']=False
    p['price_observed_on']=OBSERVED if p['unit_price'] is not None else None
    if p['price_source_id']:
        src=source_lookup[p['price_source_id']]
        p['price_source_url']=src['url']
        p['availability']=src.get('availability')
        p['tax_basis']=src.get('tax_basis')
        p['shipping_basis']=src.get('shipping_basis')
    else:
        p['price_source_url']=None
        p['availability']=None
        p['tax_basis']=None
        p['shipping_basis']=None
model['build_summary']['essential_unpriced_line_count']=len(model['build_summary']['essential_unpriced_line_ids'])

(HERE/'cost_model.json').write_text(json.dumps(model,indent=2,ensure_ascii=False)+'\n')
(HERE/'sources.json').write_text(json.dumps(dict(as_of=OBSERVED,observations=source_rows,restrictions='Links and short factual summaries only;no vendor CAD,drawings,images or full webpages redistributed.'),indent=2,ensure_ascii=False)+'\n')
fields=['id','name','sku','quantity','quantity_unit','scope','supply_kind','selection_status','acquisition_status','essential','unit_price','currency','extended_price','pricing_status','price_source_id','included_in_cost_of','unit_mass_kg','mass_basis','included_in_pinned_mass_subtotal','source_ids','notes','quote_date','is_supplier_quote','price_observed_on','price_source_url','availability','tax_basis','shipping_basis']
with (HERE/'BOM.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for p in parts:
        row={k:p.get(k) for k in fields}
        row={k:('null' if v is None else ('|'.join(v) if isinstance(v,list) else str(v).lower() if isinstance(v,bool) else v)) for k,v in row.items()}
        w.writerow(row)
print(json.dumps(dict(parts=len(parts),baskets=baskets,essential_unpriced=len(model['build_summary']['essential_unpriced_line_ids']))))
