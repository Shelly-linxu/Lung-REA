from pathlib import Path
import sys
import numpy as np,pandas as pd
from scipy.special import expit,logit
from scipy.optimize import minimize,lsq_linear
from sklearn.preprocessing import SplineTransformer,StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
V=Path(__file__).parent.parent/'NHANES_stability_v20';sys.path.insert(0,str(V.resolve()))
from direct_core import metrics
BASE=['age','male','former_smoker','current_smoker','current_cigs','zFEV','zFVC','bmi','smoking_duration_proxy']
RESP=BASE+['pef100','height','asthma','chronic_lung','cough','phlegm','wheeze']
SOCIO=RESP+['low_education','poverty_ratio']
FULL=SOCIO+['quit_years','heart_failure','heart_attack','stroke','hypertension','diabetes']
CLINICAL=FULL.copy()
LABS=['wbc', 'hemoglobin', 'rdw', 'lymph_pct', 'albumin']
FULL=CLINICAL+LABS
PANELS=[BASE,RESP,CLINICAL,RESP+LABS,FULL]
BINARY=['male','former_smoker','current_smoker','asthma','chronic_lung','cough','phlegm','wheeze','low_education','heart_failure','heart_attack','stroke','hypertension','diabetes']
CONFIGS=[dict(panel=i,interaction=j,C=c)for i in range(5)for j in [False,True]for c in [.003,.01,.1,1.,10.]]
BCONFIGS=[dict(leaves=l,leaf=n,iterations=t)for l in [3,7]for n in [50,100]for t in [100,200]]
POS=['former_smoker','current_smoker','current_cigs','smoking_duration_proxy','chronic_lung','cough','phlegm','wheeze','low_education','heart_failure','heart_attack','stroke','hypertension','diabetes']

class Expanded:
 def __init__(self,cfg):self.cfg=cfg;self.features=PANELS[cfg['panel']]
 def clean(self,d,fit=False):
  x=d[self.features].copy()
  if fit:
   self.impute={}
   for v in self.features:
    z=x.loc[x.current_smoker.eq(1),v]if v=='current_cigs'else(x.loc[x.former_smoker.eq(1),v]if v=='quit_years'else x[v]);z=z.dropna()
    self.impute[v]=float(z.mode().iloc[0]if v in BINARY else z.median())if len(z)else 0.
  for v in self.features:x[v]=x[v].fillna(self.impute[v])
  x.loc[x.current_smoker.eq(0),'current_cigs']=0
  if 'quit_years'in x:x.loc[x.former_smoker.eq(0),'quit_years']=0
  return x
 def design(self,d,fit=False):
  x=self.clean(d,fit)
  if fit:
   self.knots={v:np.quantile(x[v],[0,.25,.5,.75,1])for v in ['age','zFEV','zFVC']};self.bmi=SplineTransformer(n_knots=4,degree=3,include_bias=False,extrapolation='linear').fit(x[['bmi']])
  if fit:self.labs={v:SplineTransformer(n_knots=3,degree=3,include_bias=False,extrapolation='linear').fit(x[[v]])for v in LABS if v in x}
  out=[];names=[]
  for v in self.features:
   if v in self.knots:
    k=self.knots[v];z=x[v].to_numpy()
    for j in range(4):
     b=z-k[j]
     if j>0:b=np.maximum(b,0)
     if j<3:b=np.minimum(b,k[j+1]-k[j])
     out.append(b);names.append(v+'_interval'+str(j))
   elif v in LABS:
    z=self.labs[v].transform(x[[v]]);out.extend(z.T);names.extend(v+'_spline'+str(j)for j in range(z.shape[1]))
   elif v=='bmi':
    z=self.bmi.transform(x[['bmi']]);out.extend(z.T);names.extend('bmi_spline'+str(j)for j in range(z.shape[1]))
   else:out.append(x[v].to_numpy());names.append(v)
  if self.cfg['interaction']:
   fe=np.maximum(-x.zFEV.to_numpy(),0);fc=np.maximum(-x.zFVC.to_numpy(),0);age=(x.age.to_numpy()-50)/10;dur=x.smoking_duration_proxy.to_numpy()/10;cur=x.current_smoker.to_numpy();male=x.male.to_numpy()
   inter={'age_FEV':age*fe,'age_FVC':age*fc,'current_FEV':cur*fe,'current_FVC':cur*fc,'duration_FEV':dur*fe,'duration_FVC':dur*fc,'male_FEV':male*fe,'male_FVC':male*fc,'joint_lung_deficits':fe*fc}
   for v in ['chronic_lung','wheeze']:
    if v in x:inter[v+'_FEV']=x[v].to_numpy()*fe
   if 'diabetes'in x:inter['diabetes_BMI']=x.diabetes.to_numpy()*np.maximum((x.bmi.to_numpy()-25)/5,0)
   for v,b in inter.items():out.append(b);names.append('ix_'+v)
  z=np.column_stack(out);self.names=names
  if fit:self.scaler=StandardScaler().fit(z)
  return self.scaler.transform(z)
 def fit(self,d):
  z=self.design(d,True);a=np.column_stack([np.ones(len(d)),z]);y=d.e5.to_numpy();b=np.zeros(a.shape[1]);b[0]=logit(y.mean());bounds=[(None,None)]
  for v in self.names:
   if v.startswith('age_interval'):bo=(1e-6,None)
   elif v.startswith(('zFEV','zFVC'))or v in ['pef100','poverty_ratio','quit_years']:bo=(None,0)
   elif v.startswith('ix_')or v in POS:bo=(0,None)
   else:bo=(None,None)
   bounds.append(bo)
  def fun(b):
   zz=a@b;g=a.T@(expit(zz)-y);g[1:]+=b[1:]/self.cfg['C'];return np.logaddexp(0,zz).sum()-y@zz+.5*(b[1:]@b[1:])/self.cfg['C'],g
  op=minimize(fun,b,jac=True,bounds=bounds,method='L-BFGS-B',options={'maxiter':3000,'ftol':1e-11,'gtol':1e-6});assert op.success,op.message;self.coef=op.x;return self
 def predict(self,d):return np.clip(expit(self.coef[0]+self.design(d)@self.coef[1:]),1e-8,1-1e-8)
 def export(self):
  b=self.bmi.bsplines_[0];return dict(config=self.cfg,features=self.features,imputation=self.impute,knots={k:v.tolist()for k,v in self.knots.items()},design_names=self.names,mean=self.scaler.mean_.tolist(),scale=self.scaler.scale_.tolist(),coef=self.coef.tolist(),BMI_bspline=dict(t=b.t.tolist(),c=b.c.tolist(),k=b.k),lab_bsplines={v:dict(t=s.bsplines_[0].t.tolist(),c=s.bsplines_[0].c.tolist(),k=s.bsplines_[0].k)for v,s in self.labs.items()},no_external_update=True)

class Boost:
 def __init__(self,cfg):self.cfg=cfg;self.cleaner=Expanded(dict(panel=4,interaction=False,C=1))
 def fit(self,d):
  x=self.cleaner.clean(d,True);cs=[1 if v=='age'or v in POS else(-1 if v in ['zFEV','zFVC','pef100','poverty_ratio','quit_years']else 0)for v in FULL]
  self.model=HistGradientBoostingClassifier(max_leaf_nodes=self.cfg['leaves'],min_samples_leaf=self.cfg['leaf'],max_iter=self.cfg['iterations'],learning_rate=.03,l2_regularization=10,early_stopping=False,monotonic_cst=cs,random_state=20261027).fit(x,d.e5);return self
 def predict(self,d):return self.model.predict_proba(self.cleaner.clean(d))[:,1]

def reference(d):
 ref={};never=d.current_smoker.eq(0)&d.former_smoker.eq(0);healthy=never&d.zFEV.ge(-1.645)&d.zFVC.ge(-1.645)
 for c in ['asthma','chronic_lung','cough','phlegm','wheeze']:healthy&=d[c].eq(0)
 q=d[healthy];ref['healthy_n']=len(q);ref['height']={str(sex):float(d.loc[d.male.eq(sex),'height'].median())for sex in [0,1]}
 if len(q)>=50:
  a=np.column_stack([np.ones(len(q)),q.age,q.height,q.male]);op=lsq_linear(a,q.pef100,bounds=([-np.inf,-np.inf,-np.inf,-np.inf],[np.inf,0,np.inf,np.inf]),tol=1e-12);assert op.success;ref['PEF_coef']=op.x.tolist();ref['fallback']=False
 else:
  ref['fallback']=True;ref['PEF_median']={str(sex):float((q if len(q[q.male.eq(sex)])else d[never]).loc[lambda x:x.male.eq(sex),'pef100'].median())for sex in [0,1]}
 ref['laboratories']={str(sex):{v:float(q.loc[q.male.eq(sex),v].median())for v in LABS}for sex in [0,1]}
 return ref

def reference_rows(spec,sex):
 age=np.round(np.arange(50,79.001,.01),2);r=pd.DataFrame({v:np.zeros(len(age))for v in FULL});r['age']=age;r['male']=sex;r['bmi']=25;r['height']=spec['height'][str(sex)];r['poverty_ratio']=3
 if spec['fallback']:r['pef100']=spec['PEF_median'][str(sex)]
 else:r['pef100']=np.column_stack([np.ones(len(r)),r.age,r.height,r.male])@np.asarray(spec['PEF_coef'])
 for v in LABS:r[v]=spec['laboratories'][str(sex)][v]
 return r
