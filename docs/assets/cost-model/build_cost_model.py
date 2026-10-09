#!/usr/bin/env python3
"""Offline, deterministic C04+E05 mass/BOM/cost patch. Writes only beside this file."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import copy,csv,hashlib,json,math
HERE=Path(__file__).resolve().parent
E05='inputs/E05/main_routes_E05/'
C04='inputs/C04/'
OUTPUTS=['cost_model.json','BOM.csv','sources.json','body_composition.json','material_mass_ledger_E05.json','replacement_map.json','mass_reconciliation.json','delta_summary.json','dependency_manifest.json']
def load(f):return json.loads((HERE/f).read_text())
def write(f,x):(HERE/f).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,tol=1e-8):assert math.isclose(a,b,rel_tol=0,abs_tol=tol),(a,b)
def validate_inputs():
    manifest=load('input-manifest.json')
    for r in manifest['inputs']:assert sha(HERE/r['file'])==r['sha256'],'Frozen input changed: '+r['file']
    public=load(E05+'PUBLIC_FILES_E05.json');freeze=load(E05+'FREEZE_E05.json')
    for f,h in public['sha256'].items():assert sha(HERE/'inputs/E05'/f)==h,f
    assert freeze['manifest_SHA256']==sha(HERE/E05/'PUBLIC_FILES_E05.json')
    assert freeze['contract_SHA256']==sha(HERE/E05/'main_pair_contract_E05.json')
    for f,h in load(C04+'checksums.json').items():assert sha(HERE/C04/f)==h,('C04 baseline hash',f)
    return manifest,public,freeze

def build():
    manifest,public,freeze=validate_inputs()
    base=load(C04+'cost_model.json');model=copy.deepcopy(base)
    body=load(C04+'body_composition.json');body_before=copy.deepcopy(body)
    contract=load(E05+'main_pair_contract_E05.json');patch=load(E05+'partition_patch_E05.json')
    graph=load(E05+'main_pair_graph_E05.json');bom=load(E05+'bom_E05.json')
    cable=load(E05+'cable_source_and_scenario_E05.json');obs=load('inputs/manufacturer_cable_observation.json')
    explicit=load('inputs/explicit_material_ledger_E05.json')['parts']
    assert len(contract['parts'])==98 and len(graph['nodes'])==98
    assert {r['name'] for r in contract['parts']}=={r['name'] for r in explicit}==set(graph['nodes'])
    assert len(set(r['name'] for r in explicit))==98
    assert contract['freeze'] and not contract['electrical_operational_acceptance']
    assert not graph['complete_upstream_or_operating_electrical_system']
    assert not bom['complete_system_BOM'] and not bom['electrically_operational']
    expected_replace=['controller_battery_partition','battery_tool_partition']
    assert patch['replace_by_name']==public['replace_E04_body_names']==expected_replace
    assert patch['deck_40_bores_unchanged'] and len(patch['cutters'])==4
    selected={r['name']:r for r in body['parts']};before={r['name']:r for r in body_before['parts']}
    changes=[]
    for r in patch['volume_checks']:
        n=r['name'];old=copy.deepcopy(selected[n]);assert n in expected_replace
        assert old['material']=='aluminium' and old['density_kg_m3']==2700
        close(old['volume_mm3'],r['before_mm3'])
        close(r['before_mm3']-r['after_mm3'],r['removed_mm3'])
        new=copy.deepcopy(old);new.update(volume_mm3=r['after_mm3'],mass_kg=r['after_mm3']*old['density_kg_m3']/1e9,source='inputs/E05/main_routes_E05/partition_patch_E05.json')
        selected[n]=new
        changes.append(dict(name=n,action='replace',source_name=n,destination_name=n,old=old,new=new,known_mass_delta_kg=new['mass_kg']-old['mass_kg'],original_row='body_composed',additional_BOM_row=False))
    assert set(r['name'] for r in changes)==set(expected_replace)
    for n,r in before.items():
        if n not in expected_replace:assert r==selected[n],n
    body['parts']=[selected[r['name']] for r in body_before['parts']]
    body['modeled_original_mass_kg']=sum(r['mass_kg'] for r in body['parts'] if r['mass_kg'] is not None)
    body['composition_order'].append('E05 exactly two partition replacements')
    body['history'].append(dict(stage='E05 four M25 bores, exactly two named partition replacements; 40-hole deck unchanged',part_count=len(body['parts']),known_original_mass_kg=body['modeled_original_mass_kg']))
    body['warning']+=' E05 replaces two partitions only; eight new E05 gland/locknut representations are separate unknown-mass BOM rows. E05 stands are separate original-metal rows.'
    body_delta=body['modeled_original_mass_kg']-body_before['modeled_original_mass_kg']
    close(body_delta,sum(r['known_mass_delta_kg'] for r in changes))
    density=selected['main_base_deck_3mm']['density_kg_m3'];assert density==2700
    routes={r['id']:r for r in contract['routes']}
    assert {(r['from'],r['to']) for r in routes.values()}=={('Q0:P_OUT','LYNX:BAT+'),('Q0:N_OUT','LYNX:BAT-')}
    assert obs['article']==cable['article']=='0060001'
    assert obs['fields']['weight_kg_per_km']==cable['source_facts']['mass_kg_per_km']==724
    assert obs['fields']['copper_index_kg_per_km']==672
    rate=obs['fields']['weight_kg_per_km']/1000
    source_parts={r['name']:r for r in contract['parts']};source_bom={r.get('id'):r for r in bom['items'] if r.get('id')}
    ledger=[];new_rows=[]
    for material in explicit:
        n=material['name'];part=source_parts[n];cat=material['category'];mass=None;quantity=1;unit='each';group=None;unit_mass=None
        assert material['actual_material']==part['actual_material']==graph['nodes'][n]['actual_material']
        assert material['display_palette_must_not_supply_material'] is True
        basis='Unknown installed mass; no density applied to representation';route_id=None;length=None
        if cat=='original_aluminium_stand':
            assert material['density_kg_m3_assumed']==density and 'aluminium' in part['actual_material']
            mass=part['volume_mm3']*density/1e9;unit_mass=mass;group='E05_original_aluminium_stands';basis='Original nominal volume × matched-deck aluminium density 2700 kg/m3; alloy/temper/weld unqualified'
        elif cat=='manufacturer_cable_length':
            assert material['density_kg_m3_assumed'] is None
            route_id=n.removesuffix('_70mm2_routed_jacket');r=routes[route_id];length=r['centreline_length_mm']/1000
            close(length,source_bom[route_id]['routed_length_m']);assert not source_bom[route_id]['procurement_cut_length_released']
            assert r['full_terminal_to_terminal_jacket_route'] and not r['crimped_conductor_contact_proven'] and not r['energizable_circuit']
            quantity=length;unit='m_nominal_routed_length';unit_mass=rate;mass=length*rate;group='E05_nominal_routed_cable';basis='Manufacturer nominal 724 kg/km × geometric centreline length; excludes allowances, terminations and hardware; procurement cut length unreleased'
        else:assert material['density_kg_m3_assumed'] is None
        ledger.append(dict(material,volume_mm3=part['volume_mm3'],nominal_routed_length_m=length,nominal_cable_mass_kg_per_m=rate if route_id else None,accepted_known_mass_kg=mass,installed_mass_kg=None,mass_basis=basis,unit_price=None,currency=None,route_id=route_id,manufacturer_article_identified=material['sku'] is not None,procurement_released=False,procurement_cut_length_m=None))
        # Every source node has one BOM row. Two replacements stay in body_composed.
        row=dict(id='E05:'+n,name=n,sku=material['sku'],quantity=quantity,quantity_unit=unit,scope='vehicle',supply_kind='original_fabrication' if cat.startswith('original_') else 'purchased_candidate',selection_status='development_candidate_not_released',acquisition_status='no_purchase_or_owned_hardware_evidence',essential=True,unit_price=None,currency=None,extended_price=None,pricing_status='unpriced',price_source_id=None,included_in_cost_of=None,unit_mass_kg=unit_mass,mass_basis=basis,included_in_pinned_mass_subtotal=mass is not None,mass_group=group,source_ids=['E05_frozen_contract']+(['lapp_0060001_mass'] if route_id else []),notes='Existing E04 terminal hardware reused; not counted again. Installed/qualified mass and complete procurement cost unknown.',quote_date=None,is_supplier_quote=False,price_observed_on=None,source_step='inputs/E05/main_routes_E05/main_pair_supported_E05.step',source_step_sha256=public['sha256']['main_routes_E05/main_pair_supported_E05.step'],ledger_node=n,assembly_group='E05_main_pair',stroke_mm=None,mass_scope='known nominal subset only',availability=None,tax_basis=None,shipping_basis=None,price_source_url=None,price_reference_period=None,E05_category=cat,installed_mass_kg=None,procurement_cut_length_m=None)
        new_rows.append(row)
    counts=Counter(r['category'] for r in ledger)
    assert counts==dict(original_aluminium_stand=8,manufacturer_cable_length=2,original_clamp_material_unknown=16,commercial_fastener_unselected=64,purchased_gland=4,purchased_locknut=4),counts
    stand_mass=sum(r['accepted_known_mass_kg'] for r in ledger if r['category']=='original_aluminium_stand')
    cable_mass=sum(r['accepted_known_mass_kg'] for r in ledger if r['category']=='manufacturer_cable_length')
    close(cable_mass,cable['source_length_mass_estimate_kg'])
    # Optional legacy leads were never loaded or accepted into the C04 mass subset.
    optional=public['remove_optional_E04_lead_nodes'];runtime=load('inputs/runtime_C04/electrical-contract.json')
    runtime_names={n for m in runtime['selected_modules'] for n in m.get('source_nodes',[])}
    electrical=load(C04+'electrical_mass_selection.json')
    assert not (set(optional)&runtime_names)
    assert not(set(optional)&{r['name'] for r in electrical['parts']})
    assert not(set(optional)&{r['name'] for r in base['parts']})
    optional_policy=dict(names=optional,action='no mass/BOM removal from selected C04; do not add old leads',selected_runtime_occurrences=0,selected_mass_ledger_occurrences=0,mass_delta_kg=0.0,evidence=['inputs/runtime_C04/electrical-contract.json','inputs/runtime_C04/electrical-scene.mjs','inputs/C04/electrical_mass_selection.json'],note='Deletion list is conditional for optional overlays. They are absent from the frozen runtime and selected C04 mass ledger. No duplicate or negative lead term.')
    for p in model['parts']:
        if p['id']=='body_composed':p.update(name=p['name']+' + E05 partition bores',unit_mass_kg=body['modeled_original_mass_kg'],sku='original:composed_body_C04_E05',notes=p['notes']+' E05 replaces exactly controller_battery_partition and battery_tool_partition; deck unchanged.')
        elif p['id']=='remaining_harness':p['notes']+=' E05 adds two nominal Q0-to-Lynx cable runs and their 96 support/retention nodes as itemized rows. This residual excludes those itemized rows and reused E04 terminal hardware; allowances and unfinished branches remain unknown.'
    assert not ({p['id'] for p in new_rows}&{p['id'] for p in model['parts']})
    model['parts']+=new_rows
    groups=defaultdict(float)
    for p in model['parts']:
        if p['included_in_pinned_mass_subtotal']:groups[p['mass_group']]+=p['quantity']*p['unit_mass_kg']
    known=sum(p['quantity']*p['unit_mass_kg'] for p in model['parts'] if p['included_in_pinned_mass_subtotal'])
    delta=stand_mass+cable_mass+body_delta
    close(known,base['mass_context']['pinned_known_subset_kg']+delta)
    model.update(schema_version='2.1.0',title='C04+E05 matched UGV mass, BOM and cost candidate')
    model['configuration'].update(revision='C04_E05_R01',body_revision=model['configuration']['body_revision']+' + E05 four bores / two partition replacements',electrical_revision='E04 + E05 two geometric Q0-to-Lynx main routes')
    model['policy']['E05_material']='Use exact named explicit material ledger. Legacy steel display palette is not density evidence. E05 commercial fasteners/glands and unspecified clamps remain unknown.'
    model['mass_context'].update(pinned_known_subset_kg=known,mass_groups_kg=dict(groups),baseline_C04_known_subset_kg=base['mass_context']['pinned_known_subset_kg'],E05_known_subset_delta_kg=delta)
    model['mass_context']['warning']+=' E05 nominal routed cable length and aluminium stand estimates are included. Procurement cut allowances, 64 unselected commercial fasteners, 16 material-unspecified clamps and eight purchased gland/locknut masses remain unknown. Do not treat the known subset as installed whole-vehicle mass.'
    model['electrical_context'].update(E05_geometric_main_route_count=2,E05_route_endpoints=[dict(id=r['id'],source=r['from'],target=r['to']) for r in routes.values()],E05_conductive_crimp_contact_verified=False,E05_energizable=False)
    model['build_summary']['essential_unpriced_line_ids']=[p['id'] for p in model['parts'] if p['essential'] and p['unit_price'] is None and p['included_in_cost_of'] is None]
    model['build_summary']['essential_unpriced_line_count']=len(model['build_summary']['essential_unpriced_line_ids'])
    model['procurement_gates'].append(dict(id='E05_main_route_release',severity='safety',status='unqualified',source_id='E05_frozen_contract',message='Two geometric cable jackets only. Allowances, lugs/crimp process, ampacity, protection, clamp material/liners, commercial fasteners, gland sealing/pullout, aluminium weld qualification and upstream circuit remain unresolved. Do not energize.'))
    model['electrical_context']['temperature_limits_file']='inputs/C04/'+model['electrical_context']['temperature_limits_file']
    for key in ['file','source_file']:model['historical_model'][key]='inputs/C04/'+model['historical_model'][key]
    body['baseline_source_root']='inputs/C04/inputs/'
    model['evidence'].update(material_file='material_mass_ledger_E05.json',replacement_file='replacement_map.json',delta_file='delta_summary.json',dependency_file='dependency_manifest.json')
    model['ui_contract']['E05_status']='Separate candidate model; not integrated into the frozen C04 app/publication payload.'
    assert model['operating_cost']==base['operating_cost']
    assert model['build_summary']['public_price_baskets']==base['build_summary']['public_price_baskets']
    # Explicitly recompute baskets as a second independent check; no zero-priced unknowns.
    for basket in model['build_summary']['public_price_baskets']:
        rows=[p for p in model['parts'] if p['currency']==basket['currency'] and p['unit_price'] is not None]
        assert [p['id'] for p in rows]==basket['line_ids']
        close(float(sum((Decimal(str(p['extended_price'])) for p in rows),Decimal(0))),basket['reference_subtotal'])
    summary=dict(revision='C04+E05_R01',baseline_known_subset_kg=base['mass_context']['pinned_known_subset_kg'],partition_replacement_delta_kg=body_delta,new_original_aluminium_stands_kg=stand_mass,nominal_routed_cable_length_m=sum(r['centreline_length_mm']/1000 for r in routes.values()),nominal_routed_cable_mass_kg=cable_mass,known_subset_delta_kg=delta,candidate_known_subset_kg=known,whole_vehicle_mass_kg=None,E05_complete_installed_mass_kg=None,E05_complete_cost=None,new_source_nodes=98,replaced_body_nodes=2,net_source_node_increase=98,added_BOM_rows=98,total_BOM_rows=len(model['parts']),unresolved_E05_node_masses=88,public_price_baskets=copy.deepcopy(model['build_summary']['public_price_baskets']),priced_subset_delta_by_currency={'USD':0.0,'PLN':0.0},complete_build_cost=None,actual_cost_per_operating_hour=None,whole_rover_runtime_hours=None,operating_scenarios_changed=False,geometric_main_routes_only=2,electrical_end_to_end_complete=False,publication_status='Separate candidate; original app, C04 cost freeze and pending publication payload unchanged',warning='A zero priced-subset delta means no additional accepted prices. It does not mean E05 costs zero.')
    replacement=dict(revision='C04+E05_R01',replacement_count=2,replace_by_name=expected_replace,replacements=changes,retained_body_part_count=len(body['parts']),unchanged_body_part_count=len(body['parts'])-2,deck_40_bores_unchanged=True,deck=copy.deepcopy(selected['main_base_deck_3mm']),new_E05_nodes=[r['name'] for r in explicit],existing_E04_terminal_hardware='Reused, no duplicate purchase or density mass term',optional_local_leads=optional_policy)
    mass=dict(configuration=model['configuration'],known_subset_kg=known,whole_vehicle_mass_kg=None,groups_kg=dict(groups),body_stages=body['history'],baseline_known_subset_kg=summary['baseline_known_subset_kg'],delta=summary,rows=[dict(id=p['id'],quantity=p['quantity'],unit_mass_kg=p['unit_mass_kg'],extended_mass_kg=p['quantity']*p['unit_mass_kg'] if p['included_in_pinned_mass_subtotal'] else None,mass_group=p['mass_group'],basis=p['mass_basis']) for p in model['parts']],exclusions=model['mass_context']['warning'])
    sources=load(C04+'sources.json');sources['observations'].append(dict(obs,kind='manufacturer_catalogue',retrieved_on=obs['verified_on'],facts='Exact article 0060001: 70 mm²; 14.2 mm nominal OD; nominal weight 724 kg/km. Separate copper index is 672 kg/km. No unit price accepted.'))
    sources['observations'].append(dict(id='E05_frozen_contract',url=None,publisher='Original project E05',kind='hash_pinned_original_contract',retrieved_on='2026-10-09',file=E05+'main_pair_contract_E05.json',sha256=freeze['contract_SHA256'],is_supplier_quote=False,facts='98 added nodes, two replaced partitions, two geometric main DC jacket routes; electrically operational false.'))
    dependencies=dict(revision='C04+E05_R01',baseline_model_sha256=sha(HERE/C04/'cost_model.json'),E05_contract_sha256=freeze['contract_SHA256'],E05_public_allowlist_sha256=freeze['manifest_SHA256'],E05_zip_sha256_reference=freeze['zip_sha256'],E05_bundled_sources=public['sha256'],upstream_separately_supplied=load('inputs/upstream_dependency_verification.json'),all_bundled_inputs_manifest='input-manifest.json',normal_build_requires_network=False,normal_build_requires_CAD_kernel=False)
    for f,x in [('cost_model.json',model),('sources.json',sources),('body_composition.json',body),('material_mass_ledger_E05.json',dict(revision='E05',parts=ledger,category_counts=dict(counts),accepted_original_aluminium_mass_kg=stand_mass,accepted_nominal_cable_mass_kg=cable_mass,whole_E05_installed_mass_kg=None,policy=load('inputs/explicit_material_ledger_E05.json')['policy'])),('replacement_map.json',replacement),('mass_reconciliation.json',mass),('delta_summary.json',summary),('dependency_manifest.json',dependencies)]:write(f,x)
    fields=list(next(csv.DictReader((HERE/C04/'BOM.csv').open())).keys())+['ledger_node','E05_category','installed_mass_kg','procurement_cut_length_m']
    with (HERE/'BOM.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in model['parts']:w.writerow({k:'null' if p.get(k) is None else '|'.join(p[k]) if isinstance(p[k],list) else str(p[k]).lower() if isinstance(p[k],bool) else p[k] for k in fields})
    write('output-checksums.json',{f:sha(HERE/f) for f in OUTPUTS})
    return summary
if __name__=='__main__':print(json.dumps(build(),indent=2))
