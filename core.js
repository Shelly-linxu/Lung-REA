/* Exact browser implementation of the frozen Lung-REA additive model. No fitting. */
(function(root){'use strict';
const mandatory=['age','male','former_smoker','current_smoker','zFEV','zFVC','height','pef100'];
const binary=['male','former_smoker','current_smoker','asthma','chronic_lung','cough','phlegm','wheeze','low_education','heart_failure','heart_attack','stroke','hypertension','diabetes'];
function missing(v){return v===null||v===undefined||v==='';}
function basis(i,k,z,t){if(k===0)return t[i]<=z&&z<t[i+1]?1:0;const a=t[i+k]-t[i],b=t[i+k+1]-t[i+1];return(a?(z-t[i])/a*basis(i,k-1,z,t):0)+(b?(t[i+k+1]-z)/b*basis(i+1,k-1,z,t):0);}
function derivative(i,k,z,t){const a=t[i+k]-t[i],b=t[i+k+1]-t[i+1];return(a?k/a*basis(i,k-1,z,t):0)-(b?k/b*basis(i+1,k-1,z,t):0);}
function spline(z,s){const t=s.t,k=s.k,n=t.length-k-1,lo=t[k],hi=t[t.length-k-1],v=Math.max(lo,Math.min(hi,z));let out=Array(s.c[0].length).fill(0);for(let i=0;i<n;i++){const b=basis(i,k,v,t)+(z<lo?(z-lo)*derivative(i,k,lo,t):z>hi?(z-hi)*derivative(i,k,hi,t):0);for(let j=0;j<out.length;j++)out[j]+=b*s.c[i][j];}return out.slice(0,-1);}
function validate(input,s){for(const f of s.features){if(!(f in input))throw Error('Missing predictor column: '+f);if(!missing(input[f])&&(typeof input[f]!=='number'||!Number.isFinite(input[f])))throw Error('Invalid numeric value: '+f);}
for(const f of mandatory)if(missing(input[f]))throw Error('Required measurement missing: '+f);
for(const f of binary)if(!missing(input[f])&&![0,1].includes(input[f]))throw Error('Expected 0/1: '+f);
const bounds={age:[50,79],height:[1.2,2.1],pef100:[.6,10],current_cigs:[0,95],poverty_ratio:[0,5],wbc:[.1,200],hemoglobin:[3,25],rdw:[5,40],lymph_pct:[0,100],albumin:[.5,6]};
for(const [f,[lo,hi]]of Object.entries(bounds))if(!missing(input[f])&&(input[f]<lo||input[f]>hi))throw Error('Value outside supported range: '+f+' ('+lo+'–'+hi+')');
if(input.current_smoker+input.former_smoker>1)throw Error('Current and former smoking must be mutually exclusive');
for(const f of ['current_cigs','smoking_duration_proxy','quit_years'])if(!missing(input[f])&&input[f]<0)throw Error('Expected nonnegative value: '+f);
}
function predict(input,data){const s=data.spec;validate(input,s);let x={},imputed=[];
for(const f of s.features){x[f]=missing(input[f])?s.imputation[f]:input[f];if(missing(input[f]))imputed.push(f);}
if(x.current_smoker===0){x.current_cigs=0;imputed=imputed.filter(f=>f!=='current_cigs');}if(x.former_smoker===0){x.quit_years=0;imputed=imputed.filter(f=>f!=='quit_years');}
let d=[];for(const f of s.features){const z=x[f];if(f in s.knots){const k=s.knots[f];for(let j=0;j<4;j++){let b=z-k[j];if(j>0)b=Math.max(b,0);if(j<3)b=Math.min(b,k[j+1]-k[j]);d.push(b);}}else if(f==='bmi'||f in s.lab_bsplines){d.push(...spline(z,f==='bmi'?s.BMI_bspline:s.lab_bsplines[f]));}else d.push(z);}
if(d.length!==s.mean.length||s.config.interaction)throw Error('Unsupported model specification');
let lp=s.coef[0];for(let j=0;j<d.length;j++)lp+=(d[j]-s.mean[j])/s.scale[j]*s.coef[j+1];
const risk=Math.min(1-1e-8,Math.max(1e-8,1/(1+Math.exp(-lp)))),r=data.reference[String(x.male)];let age=null,status='within_reference_range';
if(risk<r.risk[0])status='below_reference_age_50';else if(risk>r.risk[r.risk.length-1])status='above_reference_age_79';else{let lo=0,hi=r.risk.length-1;while(hi-lo>1){const mid=(lo+hi)>>1;if(r.risk[mid]<=risk)lo=mid;else hi=mid;}age=r.age[lo]+(risk-r.risk[lo])/(r.risk[hi]-r.risk[lo])*(r.age[hi]-r.age[lo]);}
return{risk_5y:risk,lung_rea_years:age,age_gap_years:age===null?null:age-x.age,age_status:status,imputed_fields:imputed,model_inputs:x};}
const api={predict,validate,spline};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.LungREA=api;
})(typeof globalThis!=='undefined'?globalThis:this);
