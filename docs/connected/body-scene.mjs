import{applyBatteryPolarity}from'./apply-battery-polarity.mjs';
import{applyNamedPartPatch,bindServiceVisibility}from'./named-part-patch.mjs';
export async function loadConnectedBody(root,asset,{contract,basePath='./assets/connected-body/'}={}){
 if(!contract?.patches||!contract.service_groups)throw Error('Missing retained body contract');
 const [body,...deltas]=await Promise.all(['body.glb.gz',...contract.patches.map(p=>p.file)].map(f=>asset(basePath+f,'Original retained body or battery interface')));
 for(let i=0;i<deltas.length;i++)applyNamedPartPatch(body,deltas[i],contract.patches[i].changes);
 if(!contract.battery_polarity)throw Error('Missing verified battery polarity map');const polarity=applyBatteryPolarity(body,contract.battery_polarity);
 const services=bindServiceVisibility(body,contract.service_groups);
 const names=body.children.map(n=>n.name);if(new Set(names).size!==names.length)throw Error('Duplicated composed body part');
 if(contract.unused_legacy_battery_proxies.some(n=>names.includes(n)))throw Error('Obsolete battery proxy in body');
 root.add(body);return{assembly:body,contract,setServiceOpen:services.setOpen,snapshot(){return{batteryPolarityVerified:true,parts:names.length,names,service:services.snapshot(),physicalOperationQualified:false};}};
}
