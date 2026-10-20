"""Check frozen artifact identity and artificial-case scoring, without cohort data."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from predict_lung_rea import predict
P=Path(__file__).resolve().parents[2]
EXPECTED={'frozen_model.json':'964e27d44b28f5b54b4ecb7c3a72da0c8639c61c7ac759bf28353979aeb3d5ad'}
for name,digest in EXPECTED.items():
 if hashlib.sha256((P/name).read_bytes()).hexdigest()!=digest:raise AssertionError('Unexpected artifact: '+name)
cases=json.loads((P/'tests/synthetic-fixtures.json').read_text());x=pd.DataFrame([c['input']for c in cases]);out=predict(x);err=0.;age_err=0.
for i,c in enumerate(cases):
 e=c['expected'];v=out.iloc[i];err=max(err,abs(v.risk_5y-e['risk_5y']))
 if v.age_status!=e['age_status']:raise AssertionError('Age status mismatch')
 if e['lung_rea_years']is None:assert pd.isna(v.lung_rea_years)
 else:age_err=max(age_err,abs(v.lung_rea_years-e['lung_rea_years']))
assert err<1e-12 and age_err<1e-9
print(json.dumps({'synthetic_cases':len(cases),'hashes_passed':True,'maximum_risk_difference':err,'maximum_age_difference_years':age_err,'age_flags_agree':True},indent=2))
