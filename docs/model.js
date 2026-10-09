export const defaults={variant:'workshop',boundary:'kit',terrain:'firm',slope:0,payload:0,speed:1,hours:4,contacts:6,tariff:.15,chargeEfficiency:.9,maintenance:0,operator:0,massFactor:1,annualHours:1500,serviceYears:5,supervision:.25};
export const terrains={firm:{mu:.6,crr:.04},gravel:{mu:.45,crr:.08},mud:{mu:.25,crr:.12}};
export function calculate(s,data,costs={}){
 const v=data.variants[s.variant],t=terrains[s.terrain],theta=s.slope*Math.PI/180,g=9.81,mass=v.gross_mass_kg*s.massFactor+s.payload;
 const force=mass*g*(Math.sin(theta)+t.crr*Math.cos(theta));
 const torque=force*data.geometry.wheel_effective_rolling_radius_m/s.contacts;
 const traction=t.mu*mass*g*Math.cos(theta)/force,torqueMargin=v.wheel_torque_continuous_design_assumption_nm/torque;
 const kw=force*s.speed/(1000*v.drive_efficiency_assumed)+v.base_auxiliary_kw;
 const runtime=v.battery_mission_kwh/kw,range=runtime*s.speed*3.6;
 const cg=(v.gross_mass_kg*s.massFactor*v.cg_stowed_m[2]+s.payload*1.25)/mass;
 const tip=Math.atan(1.35/cg)*180/Math.PI;
 const projection=1.35-cg*Math.tan(theta);
 const gridKwh=kw*s.hours/s.chargeEfficiency;
 const capital=costs.totals_usd?.[s.variant+'_robot_hardware']?.base??0,packCost=v.battery_modules*1249.95,nonbattery=Math.max(0,capital-packCost);
 const capitalPerHour=nonbattery/(s.annualHours*s.serviceYears);
 const batteryReserve=Math.max(packCost*kw/(v.battery_nominal_kwh*.8*2000),packCost/(5*s.annualHours));
 const partsPerHour=nonbattery*.04/s.annualHours;
 const labourPerHour=s.supervision*50+10+s.operator+s.maintenance;
 const consumablesPerHour=s.variant==='field'?6:3;
 const rate=kw/s.chargeEfficiency*s.tariff+capitalPerHour+batteryReserve+partsPerHour+labourPerHour+consumablesPerHour;
 return {mass,force,torque,traction,torqueMargin,kw,runtime,range,cg,tip,projection,gridKwh,energyCost:gridKwh*s.tariff,capital,capitalPerHour,batteryReserve,partsPerHour,labourPerHour,consumablesPerHour,rate,runCost:rate*s.hours,missionKwh:kw*s.hours,battery:v.battery_mission_kwh,current:kw*1000/v.battery_voltage_nominal_v,speedPass:s.speed<=v.speed_operating_cap_m_s,energyPass:runtime>=s.hours,torquePass:torqueMargin>=1.5,tractionPass:traction>=1.25};
}
