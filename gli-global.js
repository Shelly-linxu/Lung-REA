/* GLI Global (2022), following rspiro 0.5 by Theodore Lytras.
 * JavaScript adaptation, 2026. GPL-2.0-or-later; see COPYING and THIRD_PARTY.md.
 * Deliberately preserves rspiro's floor(age*4)/4 age lookup, with exact age in logs.
 * Only ages 50–79 are implemented, matching the frozen Lung-REA model domain.
 */
(function(root){'use strict';
function convert(age,height,male,fev1,fvc,data){
for(const v of [age,height,male,fev1,fvc])if(typeof v!=='number'||!Number.isFinite(v))throw Error('Invalid raw spirometry input');
if(age<50||age>79||height<1.2||height>2.1||![0,1].includes(male))throw Error('Age, height or sex outside Lung-REA domain');
if(fev1<.5||fev1>8||fvc<.5||fvc>10)throw Error('Spirometry must be in liters: FEV1 0.5–8 L; FVC 0.5–10 L');
const sex=male===1?1:2,a=Math.floor(age*4)/4,lnA=Math.log(age),lnH=Math.log(height*100),out={};
for(const p of ['FEV1','FVC']){const r=data[`${sex}:${p}:${a}`];if(!r)throw Error('Missing GLI age lookup');let M,S,L;
if(male===1&&p==='FEV1'){M=Math.exp(-11.399108+2.462664*lnH-.011394*lnA+r[0]);S=Math.exp(-2.256278+.080729*lnA+r[1]);L=1.22703;}
else if(male===1){M=Math.exp(-12.629131+2.727421*lnH+.009174*lnA+r[0]);S=Math.exp(-2.195595+.068466*lnA+r[1]);L=.9346;}
else if(p==='FEV1'){M=Math.exp(-10.901689+2.385928*lnH-.076386*lnA+r[0]);S=Math.exp(-2.364047+.129402*lnA+r[1]);L=1.21388;}
else{M=Math.exp(-12.055901+2.621579*lnH-.035975*lnA+r[0]);S=Math.exp(-2.310148+.120428*lnA+r[1]);L=.899;}
const obs=p==='FEV1'?fev1:fvc;out[p==='FEV1'?'zFEV':'zFVC']=(Math.pow(obs/M,L)-1)/(L*S);}
return out;}
const api={convert,implementation:'GLI Global (2022), rspiro 0.5 compatible'};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.GLIGlobal=api;
})(typeof globalThis!=='undefined'?globalThis:this);
