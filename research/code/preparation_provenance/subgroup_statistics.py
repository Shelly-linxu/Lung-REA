from pathlib import Path
import pandas as pd,numpy as np,json
from sklearn.metrics import roc_auc_score
from scipy.special import expit,logit
P=Path('lung_age_study_20261019/manuscript_lung_rea_v30');V=P.parent/'lab_expanded_lung_age_v25'
x=pd.read_csv(V/'candidate_data_LOCAL_ONLY.csv');o=pd.read_csv(V/'nested_predictions_LOCAL_ONLY.csv');o=o[o.family.eq('expanded')].groupby('uid').prediction.mean();h=pd.read_csv(V/'historical_predictions_LOCAL_ONLY.csv').set_index('uid').prediction
rng=np.random.default_rng(20261031)
def measure(y,p):
 z=logit(np.clip(p,1e-8,1-1e-8));a=np.column_stack([np.ones(len(z)),z]);b=np.array([0.,1.])
 for _ in range(30):
  q=expit(a@b);H=(a.T*(q*(1-q)))@a
  try:step=np.linalg.solve(H+np.eye(2)*1e-10,a.T@(y-q))
  except:break
  b+=step
  if np.max(np.abs(step))<1e-8:break
 return [roc_auc_score(y,p)if len(np.unique(y))==2 else np.nan,np.mean((y-p)**2),y.mean(),p.mean(),y.mean()/p.mean(),b[1]]
rows=[]
for cohort,label,pred in [('NHANES_2007_2012','Development internal OOF',o),('NHANES_III','Historical frozen evaluation',h)]:
 d=x[x.cohort.eq(cohort)].copy();d['prediction']=d.uid.map(pred);assert d.prediction.notna().all()
 subsets=[('Overall','All participants',np.ones(len(d),bool)),('Sex','Female',d.male.eq(0)),('Sex','Male',d.male.eq(1))]
 subsets += [('Age',f'{lo}–{lo+9}',d.age.between(lo,lo+9))for lo in [50,60,70]]
 subsets += [('Smoking','Never',d.current_smoker.eq(0)&d.former_smoker.eq(0)),('Smoking','Former',d.former_smoker.eq(1)),('Smoking','Current',d.current_smoker.eq(1)),('FEV1','Below LLN',d.zFEV.lt(-1.645)),('FEV1','At or above LLN',d.zFEV.ge(-1.645))]
 for group,level,mask in subsets:
  g=d.loc[mask];y=g.e5.to_numpy();p=g.prediction.to_numpy();val=measure(y,p);bs=[]
  for i in range(2000):
   ix=rng.integers(len(y),size=len(y));bs.append(measure(y[ix],p[ix]))
  ci=np.nanquantile(bs,[.025,.975],axis=0);r=dict(population=label,group=group,level=level,n=len(g),deaths=int(y.sum()))
  for j,k in enumerate(['AUROC','Brier','observed','predicted','OE','slope']):r[k]=val[j];r[k+'_low']=ci[0,j];r[k+'_high']=ci[1,j]
  # Observed mortality is binomial Wilson, rather than bootstrap.
  nn=len(y);ph=y.mean();den=1+1.96**2/nn;ctr=(ph+1.96**2/(2*nn))/den;half=1.96*np.sqrt(ph*(1-ph)/nn+1.96**2/(4*nn**2))/den;r['observed_low']=ctr-half;r['observed_high']=ctr+half;rows.append(r)
  print(label,group,level,'n',len(g),'deaths',int(y.sum()),flush=True)
pd.DataFrame(rows).to_csv(P/'performance_CI_subgroups.csv',index=False)
# Audit selection between saved checkpoints; no model fitting or exclusions introduced.
f=pd.read_csv('lung_age_study_20261017/validation_v2/NHANES_flow.csv');n=pd.read_csv('lung_age_study_20261017/clinical_lung_age_v7/NH3_participant_flow.csv');m=pd.read_csv('lung_age_study_20261017/phenotype_v4/NHANES_general_phenotypes_LOCAL_ONLY.csv',low_memory=False);m=m[m.current_smoker.isin([0,1])&m.former_smoker.isin([0,1])]
flow=[]
for stage in ['spirometry_records','age50_79','core_complete_plausible','quality_A_B']:flow.append(dict(population='Development',step=stage,n=int(f.loc[f.step.eq(stage),'n'].sum())))
flow.append(dict(population='Development',step='known_smoking',n=len(m)));flow.append(dict(population='Development',step='retained_mortality_link_and_GLI',n=int(x.cohort.eq('NHANES_2007_2012').sum())))
for _,r in n.iterrows():flow.append(dict(population='Historical',step=r.step,n=int(r.n)))
flow.append(dict(population='Historical',step='retained_mortality_link_and_GLI',n=int(x.cohort.eq('NHANES_III').sum())))
pd.DataFrame(flow).to_csv(P/'participant_selection_flow.csv',index=False)
print(pd.DataFrame(flow).to_string(index=False))
