"""Frozen Lung-REA risk and age scorer. No fitting or recalibration is performed.

Inputs are engineered predictors in the units and coding of predictor_dictionary.csv.
This utility does not calculate GLI z-scores or adjudicate spirometry quality.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from score_frozen import score
P=Path(__file__).resolve().parents[2]
MANDATORY=['age','male','former_smoker','current_smoker','zFEV','zFVC','height','pef100']
BINARY=['male','former_smoker','current_smoker','asthma','chronic_lung','cough','phlegm','wheeze','low_education','heart_failure','heart_attack','stroke','hypertension','diabetes']
def public_reference():
 # model-data.js is an existing public static artifact. Parse its JSON payload;
 # no JavaScript execution or parameter estimation is involved.
 text=(P/'model-data.js').read_text()
 data=json.loads(text.split('const data=',1)[1].split(';if(typeof module',1)[0])
 return pd.concat([pd.DataFrame({'male':int(sex),'age':curve['age'],'risk5':curve['risk']})for sex,curve in data['reference'].items()],ignore_index=True)
def predict(data,model_path=None,reference_path=None):
 spec=json.loads(Path(model_path or P/'frozen_model.json').read_text());ref=pd.read_csv(reference_path) if reference_path else public_reference()
 missing=set(spec['features'])-set(data.columns)
 if missing:raise ValueError('Missing predictor columns: '+', '.join(sorted(missing)))
 x=data[spec['features']].apply(pd.to_numeric,errors='raise')
 if np.isinf(x.to_numpy()).any():raise ValueError('Infinite inputs are invalid')
 if x[MANDATORY].isna().any().any():raise ValueError('Mandatory core measurements must not be missing')
 for v in BINARY:
  if not x[v].dropna().isin([0,1]).all():raise ValueError(v+' must be 0/1 or optional missing')
 if not x.age.between(50,79).all():raise ValueError('Baseline age must be 50–79 years')
 if not x.height.between(1.2,2.1).all():raise ValueError('Height must be in meters within source eligibility')
 if not x.pef100.between(.6,10).all():raise ValueError('pef100 must be PEF/100 L/min within source eligibility')
 if (x.current_smoker+x.former_smoker>1).any():raise ValueError('Current/former smoking states must be mutually exclusive')
 for v in ['current_cigs','smoking_duration_proxy','quit_years']:
  if (x[v].dropna()<0).any():raise ValueError(v+' must be nonnegative')
 bounds={'current_cigs':(0,95),'poverty_ratio':(0,5),'wbc':(.1,200),'hemoglobin':(3,25),'rdw':(5,40),'lymph_pct':(0,100),'albumin':(.5,6)}
 for v,(lo,hi) in bounds.items():
  if not x[v].dropna().between(lo,hi).all():raise ValueError(v+' is outside the harmonized source range; check units/coding')
 pp=score(x,spec);age=np.full(len(x),np.nan);status=np.empty(len(x),dtype=object)
 for sex in [0,1]:
  r=ref[ref.male.eq(sex)].sort_values('age');rr=r.risk5.to_numpy();assert np.all(np.diff(rr)>0)
  ix=np.flatnonzero(x.male.eq(sex).to_numpy());z=pp[ix];inside=(z>=rr[0])&(z<=rr[-1]);age[ix[inside]]=np.interp(z[inside],rr,r.age);status[ix]=np.where(inside,'within_reference_range',np.where(z<rr[0],'below_reference_age_50','above_reference_age_79'))
 return pd.DataFrame({'risk_5y':pp,'lung_rea_years':age,'age_status':status},index=data.index)
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('input_csv');a.add_argument('output_csv');args=a.parse_args();data=pd.read_csv(args.input_csv);predict(data).to_csv(args.output_csv,index=False)
