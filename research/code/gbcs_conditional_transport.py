"""Conditional GBCS transport diagnostic for the unchanged final Lung-REA model.

Source data are not distributed. This code requires locally authorized GBCS files.
Income-to-poverty ratio and heart failure are scenario inputs, not observations.
PEF units and disease/questionnaire equivalence remain unverified. Results must
not be described as complete external validation. No fitting or recalibration.
"""
from pathlib import Path
import sys,json,hashlib,subprocess,warnings
import numpy as np,pandas as pd
warnings.simplefilter('ignore',UnicodeWarning)
import argparse
parser=argparse.ArgumentParser(description="Conditional GBCS transport analysis; not complete external validation. No model updating.")
parser.add_argument('--data-dir',type=Path,required=True,help='Local directory containing the authorized baseline and vital files')
parser.add_argument('--output-dir',type=Path,required=True,help='Local output directory outside the Git repository')
parser.add_argument('--pef-unit-assumption',choices=['L/s'],required=True,help='Explicit unverified assumption used in this exploratory analysis')
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
P=args.output_dir.resolve()
if P==root or root in P.parents:raise ValueError('Store generated research outputs outside the public repository')
P.mkdir(parents=True,exist_ok=True)
M=root/'research/scoring';web=root
sys.path.insert(0,str(M));from predict_lung_rea import predict
sys.path.insert(0,str(root/'research/code/NHANES_stability_v20'));from direct_core import metrics
src=args.data_dir.resolve();cols=['obje_id','phase','agec','sex','reg_date','birth','fev','fvc','height','bmi','smk','smk_am','v2_1','v2_3','v2_12','wbc','hgb','rdw','lymp','alb','pef','edu','v10_2c','v10_3c','v10_6a','v12_3a','v12_5b','v12_5f','v12_5h','v12_7b','v12_7c']
x=pd.read_stata(src/'gbcs_main.dta',columns=cols,convert_categoricals=False);flow=[]
def retain(mask,label):
 global x
 n=len(x);x=x.loc[mask].copy();flow.append(dict(step=label,retained=len(x),excluded=n-len(x)))
flow.append(dict(step='Baseline all phases',retained=len(x),excluded=0));retain(x.phase.eq(1),'Phase 1 only')
x['age']=x.reg_date.dt.year-x.birth.dt.year-((x.reg_date.dt.month*100+x.reg_date.dt.day)<(x.birth.dt.month*100+x.birth.dt.day)).astype(int)
retain(x.age.between(50,79)&(x.age-x.agec).abs().le(1)&x.sex.isin([0,1])&x.fev.between(.5,8)&x.fvc.between(.5,10)&x.height.between(120,210)&(x.fev/x.fvc).le(1.05),'Age and plausible core spirometry/height')
retain(x.smk.isin([0,2,3])&x.v2_1.ne(2),'Regular smoking categories; exclude ex-occasional/current occasional')
# PEF unit is not established by dictionary; all resulting predictions are conditional.
x['pef100']=x.pef*60/100
retain(x.pef100.between(.6,10),'PEF plausible CONDITIONAL on L/s interpretation')
retain(x.wbc.between(.1,200)&(x.hgb/10).between(3,25)&x.rdw.between(5,40)&x.lymp.between(0,100)&(x.alb/10).between(.5,6),'All five baseline laboratory values observed and plausible')
x['key']=pd.to_numeric(x.obje_id,errors='raise');assert x.key.is_unique
v=pd.read_stata(src/'newvital_2026.dta',columns=['obje_id','dead','ddate','und_icd','reg_date'],convert_categoricals=False);v['key']=pd.to_numeric(v.obje_id,errors='raise');assert v.key.is_unique
x=x.merge(v.drop(columns='obje_id').rename(columns={'reg_date':'vital_baseline'}),on='key',how='left',validate='one_to_one')
retain(x.dead.isin([0,1])&x.ddate.notna()&x.reg_date.eq(x.vital_baseline),'Known vital status, matching baseline and valid endpoint date')
x['years']=(x.ddate-x.reg_date).dt.days/365.25
anniversary=x.reg_date+pd.DateOffset(years=5)
retain(x.years.gt(0)&(x.dead.eq(1)|x.ddate.ge(anniversary)),'Positive follow-up and known five-year status')
x['e5']=(x.dead.eq(1)&x.ddate.le(x.reg_date+pd.DateOffset(years=5))).astype(int)
x['male']=x.sex;x['height']=x.height/100;x['former_smoker']=x.smk.eq(2).astype(int);x['current_smoker']=x.smk.eq(3).astype(int)
x['current_cigs']=np.where(x.current_smoker.eq(1),x.smk_am.where(x.smk_am.between(0,300)).clip(upper=95),0.)
start=x.v2_12.where(x.v2_12.between(5,x.age));quit=x.v2_3.where(x.v2_3.between(0,x.age));x['quit_years']=np.where(x.former_smoker.eq(1),quit,0.)
x['smoking_duration_proxy']=np.where(x.current_smoker.eq(1),x.age-start,np.where(x.former_smoker.eq(1),x.age-quit-start,0.));x['smoking_duration_proxy']=x.smoking_duration_proxy.where(x.smoking_duration_proxy.between(0,x.age))
x['bmi']=x.bmi.where(x.bmi.between(12,70));x['hemoglobin']=x.hgb/10;x['lymph_pct']=x.lymp;x['albumin']=x.alb/10
for dest,raw in [('asthma','v12_7c'),('chronic_lung','v12_7b'),('cough','v10_2c'),('phlegm','v10_3c'),('heart_attack','v12_5h'),('stroke','v12_5f'),('hypertension','v12_5b')]:x[dest]=x[raw].where(x[raw].isin([0,1]))
x['wheeze']=x.v10_6a.map({1:1.,2:0.});x['diabetes']=x.v12_3a.map({2:1.,1:0.});x['low_education']=np.where(x.edu.between(1,6),x.edu.le(3).astype(float),np.nan)
js='''const fs=require('fs'),g=require(process.argv[1]+'/gli-global.js'),d=require(process.argv[1]+'/gli-data.js');const x=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(x.map(r=>g.convert(r.age,r.height,r.male,r.fev,r.fvc,d))));'''
import shutil
node=shutil.which('node')
if node is None:raise RuntimeError('Node.js is required for the verified GLI conversion')
out=subprocess.run([node,'-e',js,str(web)],input=x[['age','height','male','fev','fvc']].to_json(orient='records',double_precision=15),capture_output=True,text=True,check=True)
z=pd.DataFrame(json.loads(out.stdout),index=x.index);x['zFEV']=z.zFEV;x['zFVC']=z.zFVC
rows=[];central=None;y=x.e5.to_numpy()
for pir in [1.,3.,5.]:
 for hf in [0.,1.]:
  x['poverty_ratio']=pir;x['heart_failure']=hf;p=predict(x);r=metrics(y,p.risk_5y);r.update(income_ratio_assumed=pir,heart_failure_assumed=hf,numerical_age_coverage=float(p.lung_rea_years.notna().mean()),above_79=float(p.age_status.eq('above_reference_age_79').mean()),below_50=float(p.age_status.eq('below_reference_age_50').mean()));rows.append(r)
  if pir==3 and hf==0:central=p.copy()
pd.DataFrame(rows).to_csv(P/'conditional_scenarios.csv',index=False);pd.DataFrame(flow).to_csv(P/'sample_flow.csv',index=False)
spec=json.loads((root/'frozen_model.json').read_text());pd.DataFrame([dict(predictor=c,missing=int(x[c].isna().sum()),missing_fraction=float(x[c].isna().mean()),minimum=float(x[c].min()),median=float(x[c].median()),maximum=float(x[c].max()))for c in spec['features']]).to_csv(P/'input_audit_aggregate.csv',index=False)
p=central.risk_5y.to_numpy();rng=np.random.default_rng(20261020);vals=[]
for _ in range(1000):
 ix=rng.integers(len(x),size=len(x));m=metrics(y[ix],p[ix]);vals.append([m[k]for k in ['AUROC','Brier','OE','calibration_slope','calibration_intercept']])
ci=np.quantile(vals,[.025,.975],axis=0);rr=metrics(y,p);pd.DataFrame([dict(metric=k,estimate=rr[k],lower=ci[0,j],upper=ci[1,j])for j,k in enumerate(['AUROC','Brier','OE','calibration_slope','calibration_intercept'])]).to_csv(P/'conditional_reference_profile_CI.csv',index=False)
q=pd.qcut(central.risk_5y,10,labels=False,duplicates='drop');dec=[]
for level in sorted(q.unique()):
 ix=q.eq(level);n=int(ix.sum());e=int(x.loc[ix,'e5'].sum());ph=e/n;den=1+1.96**2/n;ctr=(ph+1.96**2/(2*n))/den;half=1.96*np.sqrt(ph*(1-ph)/n+1.96**2/(4*n*n))/den;dec.append(dict(decile=int(level)+1,n=n,deaths=e,predicted=float(central.loc[ix,'risk_5y'].mean()),observed=ph,observed_low=ctr-half,observed_high=ctr+half))
pd.DataFrame(dec).to_csv(P/'conditional_reference_profile_deciles.csv',index=False)
sub=[]
for name,mask in [('Female',x.male.eq(0)),('Male',x.male.eq(1)),('Age 50-59',x.age.between(50,59)),('Age 60-69',x.age.between(60,69)),('Age 70-79',x.age.between(70,79))]:sub.append(dict(subgroup=name,**metrics(y[mask],p[mask])))
pd.DataFrame(sub).to_csv(P/'conditional_reference_profile_subgroups.csv',index=False)
checks={'analysis_type':'Conditional transport diagnostic; NOT complete external validation','PEF_units':'L/s ASSUMED, not independently verified','unobserved_predictor_scenarios':['income-to-poverty ratio','heart failure'],'model_sha256':hashlib.sha256((root/'frozen_model.json').read_bytes()).hexdigest(),'reference_sha256':json.loads((root/'model-data.js').read_text().split('const data=',1)[1].split(';if(typeof module',1)[0])['reference_sha256'],'parameter_updating':False,'individual_records_saved':False,'n':len(x),'five_year_deaths':int(y.sum()),'source_vital_file':'newvital_2026.dta','model':'Final 29-predictor C=0.003','no_manuscript_changes':True}
(P/'ANALYSIS_CHECKS.json').write_text(json.dumps(checks,indent=2));print(pd.DataFrame(flow).to_string(index=False));print(pd.DataFrame(rows)[['income_ratio_assumed','heart_failure_assumed','n','events','observed','predicted','AUROC','Brier','OE','numerical_age_coverage']].to_string(index=False));print('CIs',pd.read_csv(P/'conditional_reference_profile_CI.csv').to_string(index=False))
