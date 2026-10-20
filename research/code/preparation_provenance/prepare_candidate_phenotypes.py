from pathlib import Path
import re,json
import pandas as pd,numpy as np
O=Path('lung_age_study_20261018/shap_lung_age_v11');S=Path('lung_age_study_20261017/clinical_lung_age_v7/source')
cols=['SEQN','DMPPIR','HFA8R','HAR2','HAR11R','HAC1C','HAC1D','HAC1N','HAC1O','HAD1','HAD3','HAD4','HAF10','HAE2','HAL1','HAL3','HAL6']
t=(S/'adult.sas').read_text().split('INPUT',1)[1].split(';',1)[0];pos={m[0]:(int(m[1])-1,int(m[2]or m[1])) for m in re.findall(r'^\s+(\w+)\s+(\d+)(?:-(\d+))?\s*$',t,re.M)}
with (S/'adult.dat').open('rb') as f:rows=[[line[pos[c][0]:pos[c][1]].decode('ascii').strip() for c in cols]for line in f]
a=pd.DataFrame(rows,columns=cols).apply(pd.to_numeric,errors='coerce')
d=pd.read_csv('lung_age_study_20261018/validation_v9/mortality_GLI_LOCAL_ONLY.csv',low_memory=False)
base=['uid','SEQN','cohort','cycle','age','male','height','fev','fvc','puff','zFEV','zFVC','bmi','asthma','chronic_lung','former_smoker','current_smoker','current_cigs','time_months','death','resp_death','resp_composite','weight','stratum','psu']
x=d[base].copy();m=x.cohort.eq('NHANES_III');n=x.loc[m].merge(a,on='SEQN',validate='one_to_one');b=lambda s:s.map({1:1.,2:0.})
n['cough']=b(n.HAL1);n['phlegm']=b(n.HAL3);n['wheeze']=b(n.HAL6);n['heart_failure']=b(n.HAC1C);n['stroke']=b(n.HAC1D);n['heart_attack']=b(n.HAF10);n['hypertension']=b(n.HAE2)
n['non_skin_cancer']=b(n.HAC1O);n['diabetes']=b(n.HAD1);preg=n.HAD3.eq(1)&n.HAD1.eq(1);n.loc[preg,'diabetes']=b(n.loc[preg,'HAD4'])
n['low_education']=np.where(n.HFA8R.between(0,17),(n.HFA8R<12).astype(float),np.nan)
# SAS INPUT reads the explicit decimal in this field; no implicit division.
n['poverty_ratio']=n.DMPPIR.where(n.DMPPIR.between(0,12)).clip(upper=5)
n['start_age']=n.HAR2.where(n.HAR2.between(5,79)&n.HAR2.le(n.age));n['quit_age']=n.HAR11R.where(n.HAR11R.between(5,79)&n.HAR11R.le(n.age))
allmodern=[]
for cycle,s in [('2007-2008','E'),('2009-2010','F'),('2011-2012','G')]:
 v=x[x.cycle.eq(cycle)].copy();src=Path('NHANES_public_1999_2018')/cycle/'data'
 sources={k:pd.read_sas(src/f'{k}_{s}.xpt',format='xport') for k in ['DEMO','SMQ','MCQ','DIQ','BPQ']};sources['RDQ']=pd.read_sas(O/'source'/f'RDQ_{s}.xpt',format='xport')
 mappings={'DEMO':['DMDEDUC2','INDFMPIR'],'SMQ':['SMD030','SMD055'],'MCQ':['MCQ160B','MCQ160E','MCQ160F','MCQ220'],'DIQ':['DIQ010'],'BPQ':['BPQ020'],'RDQ':['RDQ031','RDQ050','RDQ070']}
 for k,cc in mappings.items():v=v.merge(sources[k][['SEQN']+cc],on='SEQN',how='left',validate='one_to_one')
 # MCQ160E is heart attack, MCQ160F stroke.
 for target,raw in [('cough','RDQ031'),('phlegm','RDQ050'),('wheeze','RDQ070'),('heart_failure','MCQ160B'),('heart_attack','MCQ160E'),('stroke','MCQ160F'),('hypertension','BPQ020')]:v[target]=b(v[raw])
 # Non-skin cancer cannot be harmonized from MCQ220 alone; excluded from common pool.
 v['diabetes']=v.DIQ010.map({1:1.,2:0.,3:0.});v['low_education']=np.where(v.DMDEDUC2.between(1,5),v.DMDEDUC2.le(2).astype(float),np.nan);v['poverty_ratio']=v.INDFMPIR.where(v.INDFMPIR.between(0,5))
 v['start_age']=v.SMD030.where(v.SMD030.between(5,79)&v.SMD030.le(v.age));v['quit_age']=v.SMD055.where(v.SMD055.between(5,79)&v.SMD055.le(v.age));allmodern.append(v)
y=pd.concat([n,*allmodern],ignore_index=True)
y['quit_years']=np.where(y.former_smoker.eq(1),y.age-y.quit_age,0.)
y['smoking_duration_proxy']=np.where(y.current_smoker.eq(1),y.age-y.start_age,np.where(y.former_smoker.eq(1),y.quit_age-y.start_age,0.));y.loc[y.smoking_duration_proxy.lt(0),'smoking_duration_proxy']=np.nan
y['pef100']=y.puff/100;y['t5']=y.time_months.clip(upper=60);y['e5']=(y.death.eq(1)&y.time_months.le(60)).astype(int)
mandatory=['age','male','former_smoker','current_smoker','current_cigs','zFEV','zFVC']
groups={c:[c] for c in ['bmi','asthma','chronic_lung','cough','phlegm','wheeze','low_education','poverty_ratio','quit_years','smoking_duration_proxy','heart_failure','heart_attack','stroke','hypertension','diabetes']};groups['PEF_height']=['pef100','height']
features=mandatory+[v for vs in groups.values()for v in vs]
y=y[base+['t5','e5']+list(dict.fromkeys([c for c in features if c not in base]))]
y.to_csv(O/'candidate_data_LOCAL_ONLY.csv',index=False)
audit=[]
for cohort,g in y.groupby('cohort'):
 for c in features:audit.append(dict(cohort=cohort,feature=c,n=len(g),missing=int(g[c].isna().sum()),fraction_missing=g[c].isna().mean(),minimum=g[c].min(),maximum=g[c].max()))
pd.DataFrame(audit).to_csv(O/'candidate_missingness.csv',index=False)
(O/'candidate_spec.json').write_text(json.dumps(dict(mandatory=mandatory,optional_groups=groups),indent=2))
pd.DataFrame([dict(variable=c,start_1based=pos[c][0]+1,end_1based=pos[c][1])for c in cols]).to_csv(O/'NH3_read_positions.csv',index=False)
print(pd.DataFrame(audit).query("cohort=='NHANES_III'")[['feature','fraction_missing','minimum','maximum']].to_string(index=False))
