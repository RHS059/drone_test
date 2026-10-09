import {operatingScenario} from './cost-math.js?v=costs-02';
export async function initCosts(){
 const host=document.querySelector('#cost-panel');
 if(!host)return;
 const read=async p=>{const r=await fetch(p);if(!r.ok)throw Error('Cost evidence unavailable');return r.json()};
 try{
  const [model,sources]=await Promise.all([read('./assets/cost-model/cost_model.json?v=steering-costs-01'),read('./assets/cost-model/sources.json?v=steering-costs-01')]);
  const money=(n,c='USD')=>n===null?'Unknown':new Intl.NumberFormat('en-US',{style:'currency',currency:c}).format(n);
  const $=s=>host.querySelector(s);
  $('#priced-subtotal').textContent=model.build_summary.public_price_baskets.map(b=>`${b.currency} ${money(b.reference_subtotal,b.currency)}`).join(' · ');
  $('#price-coverage').textContent=`${model.build_summary.essential_unpriced_line_ids.length} essential cost lines still need quotes. Arms, drives, fabrication, integration and destination costs are excluded from this subtotal.`;
  $('#price-date').textContent='Public listing references checked '+model.as_of+'. Listings are not firm quotes; confirm stock and bundle contents.';
  const observations=sources.observations;
  const findSource=id=>Array.isArray(observations)?observations.find(s=>s.id===id):observations[id];
  for(const p of model.parts.filter(p=>p.extended_price!==null&&p.extended_price!==undefined)){
   const source=findSource(p.price_source_id),row=document.createElement('tr');
   for(const value of [p.name,p.sku,String(p.quantity),money(p.unit_price,p.currency),money(p.extended_price,p.currency)]){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}
   const cell=document.createElement('td');if(source){const link=document.createElement('a');link.href=source.url||source.URL;link.target='_blank';link.rel='noopener';link.textContent='Listing';cell.append(link);const note=document.createElement('small');note.textContent=[source.availability,source.tax_basis].filter(Boolean).join(' · ');cell.append(note)}row.append(cell);$('#priced-parts').append(row);
  }
  for(const id of model.build_summary.essential_unpriced_line_ids){const p=model.parts.find(p=>p.id===id),li=document.createElement('li');li.textContent=p?.name??id;$('#unpriced-parts').append(li)}
  $('#mass-summary').textContent=`Modeled known subtotal: ${model.mass_context.pinned_known_subset_kg.toFixed(2)} kg. Complete vehicle mass and center of gravity remain unknown.`;
  for(const p of model.parts){const row=document.createElement('tr');const known=Number.isFinite(p.unit_mass_kg),total=known&&Number.isFinite(p.quantity)?p.unit_mass_kg*p.quantity:null;for(const value of [p.name,String(p.quantity??'Unknown'),known?p.unit_mass_kg.toFixed(3)+' kg':'Unknown',total===null?'Unknown':total.toFixed(3)+' kg',p.included_in_pinned_mass_subtotal?'Yes':'No']){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}$('#mass-parts').append(row)}
  const defaults=model.operating_cost.scenarios.find(s=>s.id==='assumed_4kw').inputs;
  const map={power:'assumed_mean_battery_kw',tariff:'assumed_tariff_usd_per_kwh',efficiency:'assumed_charging_efficiency',supervision:'assumed_supervision_hours_per_robot_hour',supervisorRate:'assumed_supervisor_usd_per_hour',maintenance:'assumed_maintenance_labor_hours_per_robot_hour',technicianRate:'assumed_technician_usd_per_hour',annualHours:'assumed_annual_operating_hours',cycles:'assumed_cycle_life',depth:'assumed_cycle_depth',calendarYears:'assumed_calendar_life_years'};
  function readNumber(k){const raw=$(`[data-cost="${k}"]`).value;if(raw.trim()==='')throw new RangeError('Enter a value for each scenario assumption.');return Number(raw)}
  function calculate(){try{const input=Object.fromEntries(Object.keys(map).map(k=>[k,readNumber(k)]));input.replacementCost=defaults.module_replacement_public_reference_usd;const result=operatingScenario(input,model.electrical_context.nominal_bank_kwh);$('#energy-cost').textContent=money(result.energy)+'/h';$('#partial-cost').textContent=money(result.partial)+'/h';$('#labor-cost').textContent=money(result.labor)+'/h';$('#battery-reserve').textContent=money(result.battery)+'/h';$('#cost-error').hidden=true;window.__COST_DEBUG__={valid:true,inputs:input,result,completeBuildCost:null,actualOperatingCost:null};}catch(e){for(const id of ['#energy-cost','#partial-cost','#labor-cost','#battery-reserve'])$(id).textContent='—';window.__COST_DEBUG__={valid:false,result:null,completeBuildCost:null,actualOperatingCost:null};$('#cost-error').hidden=false;$('#cost-error').textContent=e.message}}
  for(const[k,v]of Object.entries(map)){const element=$(`[data-cost="${k}"]`);element.value=defaults[v];element.addEventListener('input',calculate)}
  $('#reset-costs').onclick=()=>{for(const[k,v]of Object.entries(map))$(`[data-cost="${k}"]`).value=defaults[v];calculate()};calculate();host.dataset.ready='true';
 }catch(e){console.error('Cost panel initialization failed',e);const error=host.querySelector('#cost-error');error.hidden=false;error.textContent='Current cost evidence could not load. No complete build or operating total is available.';host.dataset.ready='error';}
}
