from pathlib import Path
import json,hashlib,pickle,sys,time
import numpy as np,pandas as pd
from sklearn.model_selection import StratifiedKFold,StratifiedGroupKFold
from sklearn.metrics import brier_score_loss
from core import Expanded,Boost,CONFIGS,BCONFIGS,reference,reference_rows,metrics,FULL
P=Path(__file__).parent;V=P.parent/'NHANES_stability_v20'
def parts(d,seed,n=3,group=False):
 if group:return list(StratifiedGroupKFold(n_splits=n,shuffle=True,random_state=seed).split(d,d.e5,d.group))
 return list(StratifiedKFold(n_splits=n,shuffle=True,random_state=seed).split(d,d.e5))
TUNING=[]
def select(d,ps,family,label):
 scores=[]
 for j,cfg in enumerate(CONFIGS if family=='expanded'else BCONFIGS):
  vals=[]
  for tr,te in ps:
   model=(Expanded(cfg)if family=='expanded'else Boost(cfg)).fit(d.iloc[tr]);vals.append(brier_score_loss(d.iloc[te].e5,model.predict(d.iloc[te])))
  scores.append(float(np.mean(vals)));TUNING.append(dict(context=label,family=family,candidate=j,Brier=scores[-1]))
 return int(np.argmin(scores))

def load():
 src=P/'candidate_data_LOCAL_ONLY.csv';allx=pd.read_csv(src);d=allx[allx.cohort.eq('NHANES_2007_2012')].reset_index(drop=True);d['group']=d.cycle.astype(str)+':'+d.stratum.astype(str)+':'+d.psu.astype(str);assert len(d)==4915 and d.e5.sum()==243;assert not d[['age','male','zFEV','zFVC','current_smoker','former_smoker']].isna().any().any();return d
if __name__=='__main__':
 d=load();preds=[];ageouts=[];selection=[];summary=[];start=time.time()
 pd.DataFrame({'feature':FULL,'missing':d[FULL].isna().sum().to_numpy()}).to_csv(P/'development_missingness.csv',index=False)
 for rep in range(3):
  for fold,(tr,te)in enumerate(parts(d,20261020+rep,5)):
   train=d.iloc[tr];test=d.iloc[te];ps=parts(train,20261101+rep*10+fold);ref=reference(train)
   for family in ['expanded','boost']:
    j=select(train,ps,family,f'repeat{rep+1}_outer{fold+1}');cfg=(CONFIGS if family=='expanded'else BCONFIGS)[j];m=(Expanded(cfg)if family=='expanded'else Boost(cfg)).fit(train);pp=m.predict(test);z=test[['uid','e5','age','male','group','cycle','weight']].copy();z['prediction']=pp;z['family']=family;z['repeat']=rep+1;z['fold']=fold+1;preds.append(z);selection.append(dict(design='nested',repeat=rep+1,fold=fold+1,family=family,candidate=j,config=json.dumps(cfg)))
    if family=='expanded':
     aa=np.full(len(test),np.nan);status=np.full(len(test),'',dtype=object)
     for sex in [0,1]:
      r=reference_rows(ref,sex);pr=m.predict(r);assert np.all(np.diff(pr)>0);ix=np.flatnonzero(test.male.eq(sex).to_numpy());ok=(pp[ix]>=pr.min())&(pp[ix]<=pr.max());ag=np.interp(pp[ix],pr,r.age);ag[~ok]=np.nan;aa[ix]=ag;status[ix]=np.where(ok,'within_range',np.where(pp[ix]<pr.min(),'below_50','above_79'))
     ageouts.append(pd.DataFrame(dict(uid=test.uid,repeat=rep+1,fold=fold+1,lung_age=aa,status=status)))
   pd.concat(preds).to_csv(P/'nested_predictions_LOCAL_ONLY.csv',index=False);pd.concat(ageouts).to_csv(P/'crossfit_lung_age_LOCAL_ONLY.csv',index=False);pd.DataFrame(selection).to_csv(P/'selection.csv',index=False);pd.DataFrame(TUNING).to_csv(P/'tuning.csv',index=False);print('Completed',rep+1,fold+1,'elapsed_minutes',round((time.time()-start)/60,1),flush=True)
  for family in ['expanded','boost']:
   q=pd.concat(preds);q=q[q['repeat'].eq(rep+1)&q.family.eq(family)];summary.append(dict(repeat=rep+1,family=family,**metrics(q.e5,q.prediction)))
  pd.DataFrame(summary).to_csv(P/'repeat_performance.csv',index=False)
 # Choose final primary among40regressions using contemporary-only repeated CV.
 ps=[x for rep in range(3)for x in parts(d,20261020+rep,5)];best=select(d,ps,'expanded','full_development');cfg=CONFIGS[best];m=Expanded(cfg).fit(d);ref=reference(d);rr=[]
 for sex in [0,1]:
  r=reference_rows(ref,sex);r['risk5']=m.predict(r);assert np.all(np.diff(r.risk5)>0);rr.append(r)
 pd.concat(rr).to_csv(P/'reference_curves.csv',index=False);spec=m.export();spec['selected_candidate']=best;spec['reference_spec']=ref;(P/'frozen_model.json').write_text(json.dumps(spec,indent=2));pickle.dump(m,(P/'frozen_model.pkl').open('wb'));pd.DataFrame(TUNING).to_csv(P/'tuning.csv',index=False)
 files=['frozen_model.json','frozen_model.pkl','reference_curves.csv','core.py','run.py','ANALYSIS_PLAN_EN.md','IMPLEMENTATION_AMENDMENT_EN.md'];(P/'FREEZE_MANIFEST.json').write_text(json.dumps({n:hashlib.sha256((P/n).read_bytes()).hexdigest()for n in files},indent=2));print('FINAL_PRIMARY_FROZEN',best,cfg,flush=True)
