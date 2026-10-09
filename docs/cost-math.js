// Scenario arithmetic only. Unknown inputs never become a zero-priced component.
export function operatingScenario(x, bankKwh) {
 const positive=['efficiency','annualHours','cycles','depth','calendarYears'];
 for(const k of ['power','tariff','supervision','supervisorRate','maintenance','technicianRate',...positive]) if(!Number.isFinite(x[k])||x[k]<0||(positive.includes(k)&&x[k]===0)) throw new RangeError('Invalid scenario input: '+k);
 if(x.efficiency>1||x.depth>1||!Number.isFinite(bankKwh)||bankKwh<=0)throw new RangeError('Invalid efficiency, discharge fraction or battery capacity');
 const energy=x.power/x.efficiency*x.tariff, labor=x.supervision*x.supervisorRate+x.maintenance*x.technicianRate;
 let battery=null;
 if(x.replacementCost!==null){if(!Number.isFinite(x.replacementCost)||x.replacementCost<0)throw new RangeError('Invalid replacement reference');battery=Math.max(x.replacementCost*x.power/(bankKwh*x.depth*x.cycles),x.replacementCost/(x.calendarYears*x.annualHours));}
 return {energy,labor,battery,partial:battery===null?null:energy+labor+battery,complete:null,measured:null};
}
