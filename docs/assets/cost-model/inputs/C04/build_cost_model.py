#!/usr/bin/env python3
"""Rebuild C04 costs from frozen JSON inputs, using only Python's standard library.
No network, app changes, vendor assets, purchases or currency conversions.
"""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
import copy,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent
OBSERVED='2026-10-09'
def load(name):return json.loads((HERE/'inputs'/name).read_text())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b):assert abs(a-b)<1e-7,(a,b)

def select_electrical_mass():
    raw=load('electrical_mass_ledger.json'); rows=[]; trough=[]
    for r in raw['parts']:
        x=copy.deepcopy(r); basis=r['material_basis'] or ''
        purchased_proxy=(('dimensioned copper lug' in basis) or ('approximate copper contact' in basis) or r['name']=='LYNX1000_original_max_housing_and_mount_interface')
        accepted=r['selected_after_overlay'] and r['estimated_mass_kg_each'] is not None and not purchased_proxy
        x['accepted_into_C04_known_subset']=accepted
        x['accepted_mass_kg']=r['estimated_mass_kg_each']*r['instance_quantity'] if accepted else None
        x['exclusion_reason']=None if accepted else ('superseded named geometry' if not r['selected_after_overlay'] else 'purchased representation or unknown original material; no accepted installed mass')
        rows.append(x)
        if r['asset'].endswith('aligned_trough_and_glands_E04'):
            assert r['instance_quantity']==1
            trough.append(dict(name=r['name'],material=basis or 'purchased representation',density_kg_m3=r['density_kg_m3_assumed'] if accepted else None,volume_mm3=r['volume_mm3_each'],mass_kg=x['accepted_mass_kg'],mass_basis='original material-volume estimate' if accepted else 'unknown purchased mass'))
    assert len(trough)==19
    return dict(raw_estimated_subtotal_kg=raw['selected_original_estimated_subtotal_kg'],trough_parts=trough,parts=rows,selected_nonbody_original_mass_kg=sum(r['accepted_mass_kg'] for r in rows if r['accepted_mass_kg'] is not None and not r['asset'].endswith('aligned_trough_and_glands_E04')),purchased_proxy_density_policy='Catalogue or verified installed masses only for purchased components. Exclude all copper-lug/contact approximations and full Lynx housing even if source classifier gives a numeric density.',whole_electrical_mass_kg=None)

def compose_body():
    base=load('body_R01_verification.json'); original={r['name']:r for r in base['parts']}
    density={k:v['density'] for k,v in base['material_assumptions'].items()}
    selected={};history=[]
    for r in load('body_PR01_check.json')['parts']:
        n=r['name']
        if n in original: material=original[n]['material']
        elif '_washer' in n or '_M6x20' in n:material='fastener'
        elif n.endswith(('_tapped_boss','_ledge','_welded_support')):material='aluminium'
        else:raise ValueError('Unmapped PR01 material: '+n)
        # These source-script replacements deliberately change steel placeholders to aluminium.
        if '_nutplate_' in n or re.fullmatch(r'(left|right)_service_nutclip_\d_\d',n):material='aluminium'
        selected[n]=dict(name=n,material=material,density_kg_m3=density[material],volume_mm3=r['volume_mm3'],mass_kg=r['volume_mm3']*density[material]/1e9,source='body_PR01_check.json + body_PR01_material_source.py',mass_basis='original nominal material-volume estimate')
    def state(label):history.append(dict(stage=label,part_count=len(selected),known_original_mass_kg=sum(r['mass_kg'] for r in selected.values() if r['mass_kg'] is not None)))
    state('PR01 baseline, R02 holes already included')
    patch=load('body_SO02_E04P_parts.json'); spec=load('body_SO02_E04P_selected.json')
    assert set(spec['replace_by_name'])=={r['name'] for r in patch['parts']} and len(patch['parts'])==20
    for r in patch['parts']:
        x=selected[r['name']];x.update(volume_mm3=r['volume_mm3'],mass_kg=r['volume_mm3']*x['density_kg_m3']/1e9,source='body_SO02_E04P_parts.json')
    state('SO02_E04P replaces exactly 20 named parts')
    electrical=select_electrical_mass()
    trough={r['name']:r for r in electrical['trough_parts']}
    changes=load('electrical_trough_contract.json')['changes']
    for change in changes:
        action,n=change['action'],change['name']
        if action in ('remove','replace'):assert n in selected,('trough missing old',n)
        if action=='remove':selected.pop(n)
        else:
            if action=='add':assert n not in selected,('trough duplicate',n)
            r=trough[n]
            selected[n]=dict(r,source='electrical_mass_ledger.json:trough_parts')
    assert {c['name'] for c in changes if c['action']!='remove'}==set(trough)
    state('E04 19-part trough/glands named delta; 15 original parts and 4 unknown-mass purchased representations')
    battery=load('battery_BA02_manifest.json'); assert len(battery['remove_names'])==34 and len(battery['remove_external_proxy_names'])==4
    removed=[]
    for n in battery['remove_names']:removed.append(selected.pop(n))
    rows={r['name']:r for r in battery['parts']}
    for n in battery['replace_names']:
        assert n in selected
        r=rows[n];v=r['volume_mm3'];selected[n].update(volume_mm3=v,mass_kg=v*selected[n]['density_kg_m3']/1e9,source='battery_BA02_manifest.json:replacement floor')
    state('BA02 removes 34 RELiON restraint parts and replaces battery well floor')
    return dict(schema_version='1.0',composition_order=['PR01','SO02_E04P','E04 trough','BA02'],material_policy='PR01 materials follow its source generator, including aluminium bosses/clips. No density is applied to purchased representations.',history=history,removed_battery_restraint_parts=removed,removed_external_battery_proxy_names=battery['remove_external_proxy_names'],parts=list(selected.values()),modeled_original_mass_kg=sum(r['mass_kg'] for r in selected.values() if r['mass_kg'] is not None),whole_body_installed_mass_kg=None,warning='Battery additions are separately counted in the BA02 original metal row. Battery catalogue mass is separate. Four LAPP gland/nut representations have unknown mass; do not treat this known subtotal as complete.')

def build():
    for r in json.loads((HERE/'input-manifest.json').read_text())['inputs']:
        assert sha(HERE/r['file'])==r['sha256'],'Frozen input changed: '+r['file']
    old=load('historical_C03_model.json'); oldparts={p['id']:p for p in old['parts']}
    mech=load('mechanical_mass_BOM_C04_R01.json');structure=load('structural_connections_C04_R05_manifest.json')
    assert len(structure['assembly_nodes'])==126
    freeze=load('PUBLIC_SOURCE_FREEZE_C04_R02.json'); frozen={r['path']:r['sha256'] for r in freeze['files']}
    for filename in ['mechanical_mass_BOM_C04_R01.json','structural_connections_C04_R05_manifest.json']:
        assert sha(HERE/'inputs'/filename)==frozen['mechanical/connection_completion_C04/'+filename]
    close(sum(x['mass_kg'] for x in structure['assembly_nodes']),mech['structural_geometric_mass_kg'])
    body=compose_body();battery=load('battery_BA02_manifest.json');electrical=select_electrical_mass()
    topology=load('electrical_topology_E04.json');contract=load('electrical_contract_E04.json')
    sources=[];parts=[]
    def source(id,url,publisher,kind,facts,**extra):
        sources.append(dict(id=id,url=url,publisher=publisher,kind=kind,retrieved_on=OBSERVED,facts=facts,is_supplier_quote=False,**extra));return id
    keep_sources={'ur20_quote','ur20_bundles','oem_dc_specs','oem_dc_candidate_price','gripper_price','coupling_price','coupling_routes','coupling_wrist_gate','coupling_external_route','coupling_alt_price','adapter_alt_price','drive_reference'}
    for s in load('historical_C03_sources.json')['observations']:
        if s['id'] in keep_sources:sources.append(copy.deepcopy(s))
    wheel=load('wheel_price_observations.json');victron=load('victron_price_observations.json');wc=load('wheel_candidates.json')
    source('c04_tire_price',wheel['tire']['url'],'TyreTrade','supplier_public_listing','Selected Trelleborg SK-900 12-16.5 12PR, seller SKU 35546. Manufacturer article identifier remains unverified.',**{k:wheel['tire'][k] for k in ['unit_price','currency','tax_basis','availability']},sku='seller:35546',seller_region='Poland',shipping_basis='Destination freight/import charges unquoted')
    source('c04_rim_specs',wheel['rim']['url'],'Bohnenkamp Benelux','supplier_technical_listing','Jantsa 10005240: 9.75 x 16.5, ET -70, 5 x 140, 94 mm center bore, 19.5 kg. No public numeric price.',sku='10005240',unit_price=None,currency=None)
    source('c04_tire_specs',wc['tire']['source'],'Trelleborg','manufacturer_documentation','SK-900 12-16.5 12PR TL uses 9.75-16.5 rim; catalogue diameter 831 mm, width 307 mm. Mass unknown. Tread-source revision and approved speed/load envelope unresolved.',page_1based=12)
    source('c04_nut_specs',wc['nut']['source'],'RIMA via distributor','manufacturer_authored_catalogue','RIMA 22095: M16x1.5 open nut, R14 sphere, 18 mm height, 27 mm AF. Price and installed mass unknown.',page_1based=77,sku='22095')
    source('c04_actuator_specs',load('actuator_contract_R02.json')['source'],'Thomson','manufacturer_documentation','Two Electrak HD48 B068, 200 mm, M/M COO development candidates; ledger accepts 7 kg catalogue configuration mass each. Exact order options, load, duty and installed power unqualified.')
    source('c04_spring_specs','https://eibach.com/product/1800.300.0200S','Eibach','manufacturer_documentation','Selected 1800.300.0200S spring is 3.54 kg each, six required. Original exterior spring geometry is excluded from mass; no price accepted.',sku='1800.300.0200S')
    for obs in victron['observations']:
        source('victron_'+obs['sku'],victron['source_url'],'Victron Energy LATAM','dated_manufacturer_price_list','2026 Q2 LATAM USD-C ex-VAT reference, checked 2026-10-09. Not a current US or destination-specific dealer quotation; stock, freight and import tax unknown.',sku=obs['sku'],price=obs['unit_price'],currency='USD',price_period='2026 Q2',seller_region='LATAM',tax_basis='ex VAT',shipping_basis='unknown',availability='unknown; price-list reference only',page_1based=obs['pdf_page'],source_document_sha256=victron['source_sha256'])
    source('victron_battery_specs','https://www.victronenergy.com/media/pg/Lithium_NG_battery_51,2_V/en/technical-data.html','Victron Energy','manufacturer_documentation','BAT548110620: 51.2 V, 100 Ah, 5.12 kWh and 37 kg per module. Two parallel modules provide 10.24 kWh nominal. Dry indoor location, ventilation, temperature, restraint and electrical gates remain open.',sku='BAT548110620')
    source('victron_bms_current_specs','https://www.victronenergy.com/media/pg/Lynx_Smart_BMS_NG/en/technical-specifications.html','Victron Energy','manufacturer_documentation','Lynx Smart BMS NG 1000 A unit mass is 2.7 kg in current technical specifications. Supersedes conflicting 2.5 kg in dated price list for mass accounting; maximum device rating does not qualify rover current.',sku='LYN034170310',mass_kg=2.7,conflicting_price_list_mass_kg=2.5)
    source('nrs_strap_sku','https://dh36nblqpps8a.cloudfront.net/assets/downloads/workbooks/2025_NRS_Rescue_Book.pdf','NRS','manufacturer_catalogue','NRS 60027.01.112 identifies 1-inch HD tie-down straps, 4-foot pair, Stealth Black. Two retail pairs supply four straps. SKU returned in manufacturer workbook search excerpt; full PDF fetch was size-limited. Reconfirm current ordering SKU.',sku='60027.01.112',retrieval='Manufacturer workbook indexed excerpt; current product page does not print exact selected SKU')
    source('nrs_strap_rating','https://www.nrs.com/rescue/nrs-1-hd-tie-down-straps/p4yc','NRS','manufacturer_public_listing','Purchased strap assembly WLL 500 lb and MBS 1,500 lb. Exact selected-pair price and mass unknown; price range minimum is not used. Catalogue rating does not qualify approximate buckle geometry, battery case or vehicle restraint.',unit_price=None,currency=None)
    def add(id,name,sku,quantity,kind='purchased_part',mass=None,group=None,price=None,currency=None,price_source=None,source_ids=(),notes='',essential=True,included_in=None,quantity_unit='each',**extra):
        p=dict(id=id,name=name,sku=sku,quantity=quantity,quantity_unit=quantity_unit,scope='vehicle',supply_kind=kind,selection_status='development_candidate_not_released',acquisition_status='no_purchase_or_owned_hardware_evidence',essential=essential,unit_price=price,currency=currency,extended_price=float(Decimal(str(price))*Decimal(str(quantity))) if price is not None and quantity is not None else None,pricing_status='public_reference_not_quote' if price is not None else ('included_in_bundle_no_separate_allocation' if included_in else 'unpriced'),price_source_id=price_source,included_in_cost_of=included_in,unit_mass_kg=mass,mass_basis='unknown' if mass is None else ('original material-volume estimate; not weighed' if kind=='original_fabrication' else 'catalogue mass; not weighed'),included_in_pinned_mass_subtotal=mass is not None and quantity is not None,source_ids=list(source_ids),notes=notes,mass_group=group,**extra)
        parts.append(p);return p
    for id in ['frame_R07','adapter_R04','arms','arm_controllers','grippers','couplings','gripper_cable_interface','gripper_fingertips']:
        p=copy.deepcopy(oldparts[id]);p['mass_group']='frame' if id=='frame_R07' else 'tools_and_arms';parts.append(p)
    for r in structure['assembly_nodes']:
        add('structure:'+r['node'],r['node'].replace('_',' '),'original:'+r['node'],1,'original_fabrication',r['mass_kg'],'structure',notes=mech['structural_mass_basis'],source_step=r['source_step'],source_step_sha256=r['source_sha256'],ledger_node=r['node'])
    for scope,key,qkey in [('joint_details','joint_original_and_proxy_breakdown','quantity'),('shock_details','shock_original_and_proxy_breakdown','quantity_all_six')]:
        for r in mech[key]:
            if not r['class'].startswith('original'):continue
            add(scope+':'+r['part'],r['part'].replace('_',' '),'original:'+r['part'],r[qkey],'original_fabrication',r['geometric_mass_each_kg'],scope,notes='Original detail estimate only. Purchased representations excluded. Material/grade and manufacturing qualification remain open.',density_kg_m3_assumption=r['density_kg_m3_assumption'])
    mappings=[('drives','WD220-SMAC132-050-48V-EMB-5STUDS'),('rims','10005240'),('tires','Trelleborg SK-900 12-16.5 12PR; seller 35546'),('wheel_nuts','22095'),('dampers','FOX 980-02-005'),('springs','1800.300.0200S'),('steering_actuators','HD48 B068, 200 mm, M/M, COO; remaining options unresolved'),('spherical_bearings','SKF GE20ES'),('outer_spherical_bearings','FK AIN16'),('outer_spacers','FK 16-12HB'),('tie_spacers','FK 12-10HB'),('tie_ends','FK JMX12 / JMXL12'),('tie_jam_nuts','FK SJNR12 / SJNL12'),('motor_mount_screws','M10x25'),('joint_retaining_screws','M3x10'),('bearing_retaining_screws','M5x12'),('guide_retaining_screws','M4x10'),('rack_cap_screws','M3x10'),('rack_stop_screws','M4x90 with washers/nuts')]
    assert len(mappings)==len(mech['purchased_BOM'])
    mech_ids=[]
    for (id,sku),r in zip(mappings,mech['purchased_BOM']):
        assert (id!='rims' or r['published_mass_each_kg']==19.5)
        price=1015 if id=='tires' else None
        src={'rims':['c04_rim_specs'],'tires':['c04_tire_price','c04_tire_specs'],'wheel_nuts':['c04_nut_specs'],'springs':['c04_spring_specs'],'steering_actuators':['c04_actuator_specs'],'drives':['drive_reference']}.get(id,[])
        note=r.get('includes',r.get('qualification','Exact hardware price, installed configuration and operating qualification remain unresolved.'))
        if id=='guide_retaining_screws':note+=' Nominal screw geometry is already included in original shock-detail mass; do not add a second mass allowance.'
        if id=='tires':note+=' Seller SKU matches size/model/ply description; exact manufacturer article identifier remains unverified.'
        if id=='wheel_nuts':note+=' Not bundled with the unpriced rims. B14-seat/M16-stud application approval, torque and grade remain open.'
        p=add(id,r['part'],sku,r['quantity'],mass=r['published_mass_each_kg'],group='mechanical_purchased',price=price,currency='PLN' if price is not None else None,price_source='c04_tire_price' if price else None,source_ids=src,notes=note)
        if 'handed_quantities' in r:p['handed_quantities']=r['handed_quantities']
        mech_ids.append(id)
    add('body_composed','Original body PR01 + SO02_E04P + E04 trough + BA02 floor','original:composed_body_C04',1,'original_fabrication',body['modeled_original_mass_kg'],'body',notes='Computed once per final named part in body_composition.json. Removed 34 RELiON restraints. Purchased gland representations and battery/strap geometry excluded. BA02 new metal separately counted.')
    ba_mass=battery['mass_accounting']['original_hardware_kg_excluding_replacement_floor']
    add('battery_mount_BA02','Original BA02 two trays and retention metal, excluding replacement floor','original:BA02_metal',1,'original_fabrication',ba_mass,'battery_mount',notes='Original aluminium trays plus nominal steel hardware only. Replacement well floor is in composed body. Batteries, webbing, buckles and terminal/vent proxies excluded.')
    add('batteries','Victron Lithium NG battery 51.2 V 100 Ah','BAT548110620',2,mass=37,group='battery_catalogue',price=2241,currency='USD',price_source='victron_BAT548110620',source_ids=['victron_BAT548110620','victron_battery_specs'],notes='Two parallel batteries; 10.24 kWh nominal. 2026 Q2 LATAM USD-C ex-VAT price is a dated reference, not a current destination quote. BA02 restraint, dry-location, thermal and electrical gates remain open.')
    add('battery_strap_pairs','NRS 1-inch HD tie-down straps, 4-foot pair, Stealth Black','60027.01.112',2,quantity_unit='retail pair',source_ids=['nrs_strap_sku','nrs_strap_rating'],notes='Two retail pairs supply four complete straps including buckles. Unit mass and exact pair price unknown. Four approximate buckle depictions are not four additional purchased items; strap rating does not validate vehicle restraint.',physical_strap_count=4)
    electrical_bom=load('electrical_bom_E04.json')
    for r in electrical_bom['items']:
        if r['ref']=='BAT1/BAT2':continue
        if r['ref']=='LYNX':
            add('battery_bms','Victron Lynx Smart BMS NG 1000 A M10',r['part'],r['quantity'],mass=2.7,group='electrical_catalogue',price=1020,currency='USD',price_source='victron_LYN034170310',source_ids=['victron_LYN034170310','victron_bms_current_specs'],notes='Current technical mass 2.7 kg; dated price-list 2.5 kg rejected for mass. 1000 A device rating does not expand the 180 A conditional warm-bank development ceiling.')
        elif r['ref']=='breakout_cases':
            add('electrical:'+r['ref'],r['part'],r['part'],r['quantity'],'original_fabrication',notes='Original external enclosure, not OEM connectors. Fabrication cost is within electrical original-fabrication quote scope below; no second mass counted.',included_in='electrical_original')
        else:
            add('electrical:'+r['ref'],r['part'],r['part'],r['quantity'],notes=r['status']+'. '+r.get('qualification','Exact price, purchased mass and configured application not established.'))
    # Required topology devices are grouped by their exact recorded selection; covered devices are not repeated.
    skip={'battery','two_pole_isolator','two_pole_main_isolator','battery_management','IPM_motor_and_reduction','robot_controller','steering_actuator'}
    groups=defaultdict(list)
    for ref,r in topology['parts'].items():
        if r['kind'] not in skip:groups[(r['kind'],r['part'])].append(ref)
    for (kind,sku),refs in groups.items():
        add('required:'+kind,kind.replace('_',' '),sku,len(refs),notes='E04 topology requirement: '+', '.join(refs)+'. Not a complete installed/commissioned component or qualified current path.',topology_refs=refs)
    add('electrical_original','Original selected E02/E04 supports, carriers and breakout detail','original:E02_E04_selected',1,'original_fabrication',electrical['selected_nonbody_original_mass_kg'],'electrical_original',notes='Original-only named mass ledger in inputs/electrical_mass_ledger.json, excluding trough parts counted in body and every purchased-component proxy. Complete electrical mass is unknown.')
    # Residual categories are explicitly scoped to avoid re-counting selected named devices.
    residual=[('remaining_harness','Remaining complete power/signal harness, connector kits, clamps and testing','Excludes separately listed lugs and glands; lengths/terminal kits and continuous routes unresolved.'),('charger','Qualified battery charger and charging connections','Exact grid connection, ATC-compatible charge workflow and SKU unresolved.'),('aux_converter','24/12 V auxiliary conversion and branch protection','Exact load/thermal-qualified converter quantities unresolved.'),('cooling','Remaining cooling and environmental sealing','Includes dry, ventilated battery location; installed weather/heat rejection solution unresolved.'),('safety_controls','Residual safety, e-stop and commissioning hardware','Excludes named topology controller/sensors; wiring, braking or energy sink and controls qualification unresolved.'),('tire_services','Valves, mounting, balancing and tire-service work','Not included in bare tire price.'),('steering','Residual steering controls, calibration and qualification','Excludes actuators, linkage, switches and purchased joints already itemized.'),('task_tools','Task-specific tools and workholding','No autonomous repair, replication or printer-building process demonstrated.'),('residual_mechanical_hardware','Remaining exact mechanical fastener/retainer/lubrication schedule','No blanket second allowance for hardware already represented in original detail estimates; final itemized purchase schedule incomplete.')]
    for id,name,note in residual:add(id,name,None,None,notes=note)
    for id in ['build_labor','engineering_nre','logistics_tax','external_workcell']:
        p=copy.deepcopy(oldparts[id]);p['mass_group']=None;parts.append(p)
    sources_by_id={s['id']:s for s in sources}
    for p in parts:
        p['quote_date']=None;p['is_supplier_quote']=False
        p['price_observed_on']=OBSERVED if p['unit_price'] is not None else None
        for k in ['source_step','source_step_sha256','ledger_node','assembly_group','stroke_mm','mass_scope']:p.setdefault(k,None)
        s=sources_by_id.get(p['price_source_id'],{})
        for k in ['availability','tax_basis','shipping_basis']:p[k]=s.get(k)
        p['price_source_url']=s.get('url');p['price_reference_period']=s.get('price_period')
    baskets=[]
    for currency in sorted({p['currency'] for p in parts if p['unit_price'] is not None}):
        chosen=[p for p in parts if p['currency']==currency and p['unit_price'] is not None]
        baskets.append(dict(currency=currency,reference_subtotal=float(sum((Decimal(str(p['extended_price'])) for p in chosen),Decimal(0))),line_ids=[p['id'] for p in chosen],line_count=len(chosen),complete_build_total=False,tax_basis='PLN tire listing gross/brutto' if currency=='PLN' else 'Mixed references: US gripper/coupling tax basis unresolved; LATAM battery/BMS ex VAT',shipping_total=None,price_scope='Dated reference subtotal only; no common destination, supplier quote, FX or checkout total'))
    old_operating=copy.deepcopy(old['operating_cost']);scenarios=[]
    for prior in old_operating['scenarios']:
        scenario=copy.deepcopy(prior);i=scenario['inputs'];i['module_replacement_public_reference_usd']=4482;i['module_price_basis']='2026 Q2 LATAM USD-C ex-VAT reference for two BAT548110620; not a current installed replacement quote'
        power=i['assumed_mean_battery_kw'];energy=power/i['assumed_charging_efficiency']*i['assumed_tariff_usd_per_kwh'];cycle=4482*power/(10.24*i['assumed_cycle_depth']*i['assumed_cycle_life']);calendar=4482/(i['assumed_calendar_life_years']*i['assumed_annual_operating_hours']);reserve=max(cycle,calendar);labor=i['assumed_supervision_hours_per_robot_hour']*i['assumed_supervisor_usd_per_hour']+i['assumed_maintenance_labor_hours_per_robot_hour']*i['assumed_technician_usd_per_hour']
        scenario['outputs'].update(energy_only_usd_per_operating_hour=energy,battery_module_cycle_reserve_usd_per_operating_hour=cycle,battery_module_calendar_reserve_usd_per_operating_hour=calendar,battery_module_reserve_usd_per_operating_hour=reserve,modeled_partial_usd_per_operating_hour=energy+labor+reserve,modeled_partial_usd_per_assumed_year=(energy+labor+reserve)*i['assumed_annual_operating_hours'])
        scenario['limits']='Analyst scenario only. Mean demand, charging efficiency, labor, 2,000 cycles, 80% depth, five years and utilization remain assumptions. Battery price is dated LATAM module-only reference. Nominal 10.24 kWh is not usable energy. Neither 180 A warm ceiling nor scenario draw validates motor/arm duty, temperature, regen, uninterrupted runtime or operating safety.'
        scenarios.append(scenario)
    old_operating['scenarios']=scenarios
    known=sum(p['quantity']*p['unit_mass_kg'] for p in parts if p['included_in_pinned_mass_subtotal'])
    mass_groups=defaultdict(float)
    for p in parts:
        if p['included_in_pinned_mass_subtotal']:mass_groups[p['mass_group']]+=p['quantity']*p['unit_mass_kg']
    close(mass_groups['mechanical_purchased'],152.24)
    close(mass_groups['structure'],mech['structural_geometric_mass_kg']);close(mass_groups['joint_details'],mech['joint_original_geometric_mass_kg']);close(mass_groups['shock_details'],mech['shock_original_steel_geometric_mass_kg'])
    gates=[dict(id='c04_wheel_interface',severity='qualification',status='unqualified',source_id='c04_rim_specs',message='B14-seat/M16-stud application approval, bearing offset load, full rim section, tire speed/load and stud/nut grade/torque remain open.'),dict(id='battery_restraint_and_environment',severity='safety',status='unqualified',source_id='victron_battery_specs',message='BA02 nominal contact and extraction geometry do not establish case preload, restraint loads, dry indoor battery location, thermal control or safe lifting of 37 kg modules.'),dict(id='battery_current_and_controls',severity='safety',status='not_enforced',source_id=None,message='180 A is a conditional warm-bank development ceiling, not a commissioned rating. Derate by both pack temperatures and actual BMS DCL/CCL. Pack loss requires validated stop; ATC/ATD, regen inhibition, independent brake/sink, branch protection and current sharing remain incomplete.'),dict(id='steering_force_duty',severity='qualification',status='unqualified',source_id='c04_actuator_specs',message='B068 exact order options, force/duty, motor-supply power and six-corner steering response are unqualified.'),dict(id='source_prices',severity='procurement',status='references_only',source_id='victron_BAT548110620',message='No supplier quotes or stock allocations. Reconfirm exact SKUs, package contents, destination taxes, import costs and freight. LATAM 2026 Q2 prices are not current US quotes.')]
    gates += [copy.deepcopy(g) for g in old['procurement_gates'] if g['id'] in ['coupling_electrical_route','arm_controller_package','original_manufacturing']]
    model=dict(schema_version='2.0.0',title='C04 six-wheel UGV matched build and operating cost reference',as_of=OBSERVED,configuration=dict(revision='C04_R01',structural_revision='C04_R05',mechanical_public_freeze='C04_R02',steering_corner_count=4,middle_corner_count=2,rack_count=2,frame_revision='R07',body_revision='PR01 + SO02_E04P + E04 trough + BA02',battery_revision='BA02',electrical_revision='E04',tool_adapter_revision='R04',not_fabrication_released=True),policy=dict(unknown_numeric='null, never zero',csv_null='literal null',public_prices='Dated reference observations, never quotes or landed totals',source_currency='Native currency baskets; no FX',proxy_mass='Purchased external proxy volumes never supply installed component mass',bundle_accounting='Two NRS pairs supply four straps including buckles; arm/controller packages count once; repeated topology references do not add duplicate purchased devices'),parts=parts,alternatives=[copy.deepcopy(x) for x in old['alternatives'] if x['id'] in ['oem_dc_200143','wrist_coupling_077','purchased_ur20_adapter']],build_summary=dict(status='incomplete_essential_items_unpriced',complete_build_cost=None,currency=None,public_price_baskets=baskets,essential_unpriced_line_ids=[p['id'] for p in parts if p['essential'] and p['unit_price'] is None and p['included_in_cost_of'] is None],excluded_from_public_baskets=['original fabrication','six exact WD220 drives','two UR20 arms and exact controller package','Jantsa rims','NRS straps','essential electrical integration, harness and services','destination tax/import/freight','unselected alternatives'],new_vs_used='No used/refurbished substitution; exact condition and package scope must be confirmed.'),mass_context=dict(pinned_known_subset_kg=known,whole_vehicle_mass_kg=None,source_snapshot_mass_kg=None,source_snapshot_corner_revision='C04 structural R05',reconciliation_method='Recomputed from frozen named ledgers; no claim that this calculation is an independent weighed or audited source snapshot',mass_groups_kg=dict(mass_groups),original_running_gear_subtotal_kg=mass_groups['structure']+mass_groups['joint_details']+mass_groups['shock_details'],accepted_rim_net_mass_kg=117,additional_catalog_nuts_kg=None,additional_catalog_nuts_in_pinned_subset=False,no_recomputed_complete_mass=True,warning='Known modeled/catalogue subtotal, not weighed or complete. Drives, tires, nuts, straps/buckles, dampers, bearings and most installed electrical components remain unknown. Named patches replace prior geometry; density is never applied to purchased representations.'),electrical_context=dict(nominal_bank_kwh=10.24,battery_count=2,battery_nominal_ah_each=100,nominal_voltage=51.2,drive_count=6,steering_actuator_count=2,steering_actuator_order_released=False,measured_steering_power_kw=None,steering_power_budget_kw=None,steering_duty_qualified=False,drive_rating_kw_each=2.2,drive_rating_duty='S2 60 min; S1 unknown',motor_current_A_each=47,motor_current_basis='motor phase/nameplate rating; not established DC bus demand',DC_bus_current_basis_verified=False,development_current_cap_A=180,cap_enforced=False,cap_condition='Two online warm packs, temperature/current-sharing/BMS DCL/CCL constraints satisfied; enforcement and braking not commissioned',system_current_rating_A=None,simultaneous_mechanical_rating_kw=13.2,ideal_minimum_DC_current_A_at_nominal_voltage=13.2*1000/51.2,full_nameplate_traction_min_bus_A_at44p8V_eta80=contract['full_nameplate_traction_min_bus_A_at44p8V_eta80'],temperature_limits_file='inputs/electrical_temperature_limits.json',regen_permission_path=topology['ATC_regen_permission_path'],load_permission_path=topology['ATD_load_permission_path'],electrical_end_to_end_complete=False,warning='10.24 kWh is nominal energy only. 180 A is conditional warm-bank development ceiling, not rated full-six-motor capability. 47 A motor phase rating is not DC demand. Cold/hot limits, pack loss, auxiliaries, UR inrush, regen and ATC/ATD control gates can further reduce or disable operation.'),procurement_gates=gates,operating_cost=old_operating,historical_model=dict(status='superseded_C03_R03_not_selected',file='inputs/historical_C03_model.json',source_file='inputs/historical_C03_sources.json',removed=['Six EVO rims and their EUR 2,891.34 basket','Six BFGoodrich tires','Four RELiON batteries and their active recall procurement gate','Six old wheel-pattern adapters/proposed output studs','Old C03/C02 structures and B045 steering candidate','Old 6.144 kWh capacity and battery reserve price'],baseline_included=False),evidence=dict(source_file='sources.json',bom_file='BOM.csv',mass_file='mass_reconciliation.json',body_file='body_composition.json',input_manifest='input-manifest.json'),ui_contract=dict(build_headline='Complete build cost: unknown',basket_label='Priced subset only; native currencies; mixed dated reference markets',operating_headline='Measured operating cost: unknown',scenario_label='Assumptions-only partial operating scenario',must_replace_old_static_text=['EUR rim VAT notice','RELiON recall notice as current selection','EVO/BFG descriptions','4-battery/6.144 kWh references'],do_not_display=['historical price baskets as current','null as zero','any combined USD/PLN or FX total','180 A as commissioned bank rating','47 A phase current as DC demand','S2 as continuous duty','whole-rover runtime prediction']))
    model['build_summary']['essential_unpriced_line_count']=len(model['build_summary']['essential_unpriced_line_ids'])
    write('cost_model.json',model);write('sources.json',dict(as_of=OBSERVED,observations=sources,restrictions='Factual summaries and links only. No raw vendor CAD, PDFs or fetched webpages.'))
    write('body_composition.json',body);write('electrical_mass_selection.json',electrical)
    write('mass_reconciliation.json',dict(configuration=model['configuration'],known_subset_kg=known,whole_vehicle_mass_kg=None,groups_kg=dict(mass_groups),body_stages=body['history'],mechanical_purchased_mass_kg=152.24,rows=[dict(id=p['id'],quantity=p['quantity'],unit_mass_kg=p['unit_mass_kg'],extended_mass_kg=p['unit_mass_kg']*p['quantity'] if p['included_in_pinned_mass_subtotal'] else None,mass_group=p.get('mass_group'),basis=p['mass_basis']) for p in parts],exclusions=model['mass_context']['warning']))
    fields=['id','name','sku','quantity','quantity_unit','scope','supply_kind','selection_status','essential','unit_price','currency','extended_price','pricing_status','price_source_id','included_in_cost_of','unit_mass_kg','mass_basis','included_in_pinned_mass_subtotal','mass_group','source_ids','notes','quote_date','is_supplier_quote','price_observed_on','price_reference_period','price_source_url','availability','tax_basis','shipping_basis']
    with (HERE/'BOM.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in parts:w.writerow({k:'null' if p.get(k) is None else '|'.join(p[k]) if isinstance(p[k],list) else str(p[k]).lower() if isinstance(p[k],bool) else p[k] for k in fields})
    print(json.dumps(dict(rows=len(parts),baskets=baskets,known_mass_kg=known,scenarios=[s['outputs']['modeled_partial_usd_per_operating_hour'] for s in scenarios]),indent=2))
    return model
if __name__=='__main__':build()
