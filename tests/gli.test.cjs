const assert=require('node:assert/strict'),gli=require('../gli-global.js'),data=require('../gli-data.js'),cases=require('./gli-reference-fixtures.json');let max=0;
for(const c of cases){const q=gli.convert(c.age,c.height,c.male,c.fev1_l,c.fvc_l,data);for(const k of ['zFEV','zFVC']){const e=Math.abs(q[k]-c[k]);max=Math.max(max,e);assert(e<1e-12,`${k}: ${e}`);}}
for(const vals of [[49,1.7,0,3,4],[80,1.7,0,3,4],[60,1.7,2,3,4],[60,1.7,0,3000,4000],[60,1.7,0,NaN,4],[60,1.7,0,0,4]])assert.throws(()=>gli.convert(...vals,data));
console.log(JSON.stringify({synthetic_cases:cases.length,max_z_absolute_error:max,guard_checks_pass:true}));
