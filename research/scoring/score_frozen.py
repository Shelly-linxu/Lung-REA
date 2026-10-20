"""Standalone frozen final additive model; no training or external updating."""
import json
import numpy as np
from scipy.special import expit
from scipy.interpolate import BSpline

def score(data,spec):
 if not isinstance(spec,dict):spec=json.load(open(spec))
 assert not spec['config']['interaction'],'This scorer implements the frozen additive model.'
 x=data[spec['features']].copy()
 for v in x:x[v]=x[v].fillna(spec['imputation'][v])
 x.loc[x.current_smoker.eq(0),'current_cigs']=0
 if 'quit_years'in x:x.loc[x.former_smoker.eq(0),'quit_years']=0
 out=[]
 for v in spec['features']:
  z=x[v].to_numpy()
  if v in spec['knots']:
   k=spec['knots'][v]
   for j in range(4):
    b=z-k[j]
    if j>0:b=np.maximum(b,0)
    if j<3:b=np.minimum(b,k[j+1]-k[j])
    out.append(b)
  elif v=='bmi'or v in spec.get('lab_bsplines',{}):
   b=spec['BMI_bspline']if v=='bmi'else spec['lab_bsplines'][v];t=np.array(b['t']);bs=BSpline(t,np.array(b['c']),b['k']);lo=t[b['k']];hi=t[-b['k']-1];zz=bs(np.clip(z,lo,hi));zz+=np.minimum(z-lo,0)[:,None]*bs(lo,nu=1)+np.maximum(z-hi,0)[:,None]*bs(hi,nu=1);out.extend(zz[:,:-1].T)
  else:out.append(z)
 z=(np.column_stack(out)-spec['mean'])/spec['scale'];return np.clip(expit(spec['coef'][0]+z@np.array(spec['coef'][1:])),1e-8,1-1e-8)
