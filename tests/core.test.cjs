const assert=require('node:assert/strict'),data=require('../model-data.js'),core=require('../core.js'),cases=require('./synthetic-fixtures.json');
for(const {input,expected}of cases){const r=core.predict(input,data);assert(Math.abs(r.risk_5y-expected.risk_5y)<1e-12);assert.equal(r.age_status,expected.age_status);if(expected.lung_rea_years===null)assert.equal(r.lung_rea_years,null);else assert(Math.abs(r.lung_rea_years-expected.lung_rea_years)<1e-9);}
for(const [k,v]of [['age',80],['age',49],['male',2],['height',170],['albumin',42],['current_cigs',100],['zFEV',null],['zFVC',Infinity]]){assert.throws(()=>core.predict({...cases[1].input,[k]:v},data));}
assert.throws(()=>core.predict({...cases[1].input,current_smoker:1,former_smoker:1},data));const noColumn={...cases[1].input};delete noColumn.wbc;assert.throws(()=>core.predict(noColumn,data));
console.log('PASS: 80 synthetic Python reference cases, bounds, required fields and mutually exclusive smoking.');
