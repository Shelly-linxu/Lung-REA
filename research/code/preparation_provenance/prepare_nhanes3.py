from pathlib import Path
import re,json,hashlib
import numpy as np,pandas as pd
O=Path('lung_age_study_20261017/clinical_lung_age_v7');S=O/'source'
def fwf(stem,cols):
 text=(S/f'{stem}.sas').read_text();text=text.split('INPUT',1)[1].split(';',1)[0]
 positions={m[0]:(int(m[1])-1,int(m[2] or m[1])) for m in re.findall(r'^\s+(\w+)\s+(\d+)(?:-(\d+))?\s*$',text,re.M)}
 assert set(cols)<=set(positions),set(cols)-set(positions)
 specs=[positions[c] for c in cols];file=S/('exam_complete.dat' if stem=='exam' else 'adult.dat');expected=195090426 if stem=='exam' else 67107314
 assert file.stat().st_size==expected,(file,file.stat().st_size)
 # Parse only requested columns, preserving independent SAS locations for auditing.
 rows=[];lengths=set()
 with file.open('rb') as f:
  for line in f:
   lengths.add(len(line));rows.append([line[a:b].decode('ascii').strip() for a,b in specs])
 z=pd.DataFrame(rows,columns=cols).apply(pd.to_numeric,errors='coerce');assert z.SEQN.is_unique
 pd.DataFrame([{'file':stem,'variable':c,'start_1based':positions[c][0]+1,'end_1based':positions[c][1]} for c in cols]).to_csv(O/f'{stem}_read_positions.csv',index=False)
 print(stem,len(z),'line_lengths',lengths,flush=True);return z
a=fwf('adult',['SEQN','HSSEX','HSAGEIR','DMARETHN','WTPFEX6','SDPSTRA6','SDPPSU6','HAR1','HAR3','HAR4S','HAC1E','HAC1F','HAC1G'])
e=fwf('exam',['SEQN','WTPFEX6','SDPSTRA6','SDPPSU6','BMPHT','BMPBMI','BMPHTFLG','BMPWTFLG','MXPAXTMR','SPPFEV1','SPPFVC','SPPPEAK','SPPTYPE','SPPREPRO','SPPRELIA','SPPMANEU'])
e[['SEQN','WTPFEX6','SDPSTRA6','SDPPSU6']].to_csv(O/'NH3_design_universe_LOCAL_ONLY.csv',index=False)
e=e.drop(columns=['WTPFEX6','SDPSTRA6','SDPPSU6'])
z=a.merge(e,on='SEQN',how='left',validate='one_to_one');flow=[]
def rec(step):flow.append({'cohort':'NHANES_III','step':step,'n':len(z)})
rec('household_adults');z['id']=z.SEQN.astype(int);z['age']=z.HSAGEIR;z['male']=z.HSSEX.map({1:1,2:0});z['height']=z.BMPHT/100;z['bmi']=z.BMPBMI.where(z.BMPBMI.between(12,70));z['fev']=z.SPPFEV1/1000;z['fvc']=z.SPPFVC/1000;z['puff']=z.SPPPEAK*.06
z=z[z.age.between(50,79)].copy();rec('age50_79')
z=z[z.height.between(1.2,2.1)&z.fev.between(.5,8)&z.fvc.between(.5,10)&z.puff.between(60,1000)&z.male.isin([0,1])].copy();rec('core_plausible')
z=z[z.SPPTYPE.eq(1)&z.SPPRELIA.eq(1)&z.SPPREPRO.eq(4)&z.SPPMANEU.between(2,16)].copy();rec('MEC_reliable_both_reproducible_2plus')
z=z[z.BMPHTFLG.eq(0)].copy();rec('directly_measured_unsubstituted_height');z['bmi']=z.bmi.where(z.BMPWTFLG.eq(0))
status=np.select([z.HAR1.eq(2),z.HAR1.eq(1)&z.HAR3.eq(2),z.HAR1.eq(1)&z.HAR3.eq(1)],[0,1,2],default=np.nan)
z['former_smoker']=np.where(np.isnan(status),np.nan,(status==1).astype(float));z['current_smoker']=np.where(np.isnan(status),np.nan,(status==2).astype(float));z=z[z.current_smoker.notna()].copy();rec('known_smoking')
z['current_cigs']=np.where(z.current_smoker==0,0,z.HAR4S.where(z.HAR4S.between(1,140)).clip(upper=95));z['asthma']=z.HAC1E.map({1:1.,2:0.});z['chronic_lung']=np.where(z.HAC1F.eq(1)|z.HAC1G.eq(1),1,np.where(z.HAC1F.eq(2)&z.HAC1G.eq(2),0,np.nan))
z['weight']=z.WTPFEX6;z['stratum']=z.SDPSTRA6;z['psu']=z.SDPPSU6;z['cycle']='1988-1994';z['cohort']='NHANES_III'
z=z[z.weight.gt(0)&z.stratum.notna()&z.psu.notna()].copy();rec('positive_MEC_weight_design');assert z.id.is_unique
z.to_csv(O/'NHANES_III_prepared_LOCAL_ONLY.csv',index=False);pd.DataFrame(flow).to_csv(O/'NH3_participant_flow.csv',index=False)
cols=['fev','fvc','puff','height','male','former_smoker','current_smoker','current_cigs','bmi','asthma','chronic_lung'];pd.DataFrame([{'variable':c,'n':len(z),'missing_n':int(z[c].isna().sum()),'median':z[c].median(),'p01':z[c].quantile(.01),'p99':z[c].quantile(.99)} for c in cols]).to_csv(O/'NH3_feature_audit.csv',index=False)
manifest=[]
for name,url in [('adult.dat','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/adult.dat'),('exam_complete.dat','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/exam.dat'),('adult.sas','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/adult.sas'),('exam.sas','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/exam.sas'),('adult_codebook.pdf','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/ADULT-acc.pdf'),('exam_codebook.pdf','https://wwwn.cdc.gov/nchs/data/nhanes3/1a/exam-acc.pdf'),('mortality_bundle.zip','https://stacks.cdc.gov/view/cdc/117141/cdc_117141_DS3.zip')]:
 p=S/name
 if p.exists():manifest.append({'file':name,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(S/'download_manifest.json').write_text(json.dumps(manifest,indent=2));print(pd.DataFrame(flow).to_string(index=False))
