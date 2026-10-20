from pathlib import Path
import pandas as pd,numpy as np,re
root=Path.cwd();p=root/'lung_age_study_20261019/lab_expanded_lung_age_v25';v=p.parent/'expanded_lung_age_v24'
plan='''# Laboratory expansion: prospectively saved analysis amendment

Use the existing modern NHANES development cohort and unchanged repeated nested cross-validation. Add white blood cell count, hemoglobin, red cell distribution width, lymphocyte percentage and serum albumin, harmonized by units to NHANES III. Exclude cycle-unavailable CRP, fasting-dependent glucose and unverified creatinine assay harmonization. Five predictor panels: original nine, respiratory sixteen, full clinical twenty-four, respiratory plus five laboratories, and full clinical plus five laboratories. Each is evaluated with or without the previously specified interactions and ridge C=0.003,0.01,0.1,1,10. Model laboratory nonlinearities using training-only cubic splines with three knots. All preprocessing, tuning and final selection use development data only, with Brier score as primary selection criterion. Healthy reference laboratory values are development-only sex-specific medians. Freeze before historical scoring; no external recalibration or selection by historical results. Expanded blood markers may reflect general health, so better mortality prediction alone cannot establish pulmonary specificity. Report unsuccessful comparisons as well as successful ones. Historical cohorts have been inspected previously and are not untouched confirmatory samples.
'''
(p/'ANALYSIS_PLAN_EN.md').write_text(plan);(p/'IMPLEMENTATION_AMENDMENT_EN.md').write_text('The laboratory branch uses the same validation design as v24; boosting is an exploratory risk benchmark, not an invertible age model.\n')
mapping={'wbc':('WCPSI','LBXWBCSI',.1,200),'hemoglobin':('HGP','LBXHGB',3,25),'rdw':('RWP','LBXRDW',5,40),'lymph_pct':('LMPPCNT','LBXLYPCT',0,100),'albumin':('AMP','LBXSAL',.5,6)}
sas=(p/'source/lab.sas').read_text();inp=sas.split('INPUT',1)[1].split(';',1)[0];pos={n:(int(a)-1,int(b or a))for n,a,b in re.findall(r'^\s+(\w+)\s+(\d+)(?:-(\d+))?\s*$',inp,re.M)}
cols=['SEQN']+[q[0]for q in mapping.values()];nh=pd.read_fwf(p/'source/lab_LOCAL_ONLY.dat',colspecs=[pos[c]for c in cols],names=cols,dtype=str);nh=nh.apply(pd.to_numeric,errors='coerce');nh=nh.rename(columns={q[0]:k for k,q in mapping.items()});nh['cohort']='NHANES_III';pieces=[nh]
for cycle,suffix in [('2007-2008','E'),('2009-2010','F'),('2011-2012','G')]:
 base=root/'NHANES_public_1999_2018'/cycle/'data';a=pd.read_sas(base/f'CBC_{suffix}.xpt',format='xport');b=pd.read_sas(base/f'BIOPRO_{suffix}.xpt',format='xport');q=a[['SEQN']+[z[1]for k,z in mapping.items()if k!='albumin']].merge(b[['SEQN','LBXSAL']],on='SEQN',validate='one_to_one');q=q.rename(columns={z[1]:k for k,z in mapping.items()});q['cohort']='NHANES_2007_2012';pieces.append(q)
lab=pd.concat(pieces,ignore_index=True)
# Modern SEQN globally unique across cycles.
assert not lab.duplicated(['cohort','SEQN']).any()
for k,(_,_,lo,hi)in mapping.items():lab.loc[~lab[k].between(lo,hi),k]=np.nan
src=root/'lung_age_study_20261018/shap_lung_age_v11/candidate_data_LOCAL_ONLY.csv';d=pd.read_csv(src).merge(lab,on=['cohort','SEQN'],how='left',validate='many_to_one');d.to_csv(p/'candidate_data_LOCAL_ONLY.csv',index=False)
qa=[]
for cohort,g in d.groupby('cohort'):
 for k in mapping:
  z=g[k];qa.append(dict(cohort=cohort,feature=k,n=len(g),missing=int(z.isna().sum()),minimum=z.min(),median=z.median(),maximum=z.max()))
pd.DataFrame(qa).to_csv(p/'laboratory_QA.csv',index=False)
s=(v/'core.py').read_text();s=s.replace('PANELS=[BASE,RESP,SOCIO,FULL]','CLINICAL=FULL.copy()\nLABS='+repr(list(mapping))+'\nFULL=CLINICAL+LABS\nPANELS=[BASE,RESP,CLINICAL,RESP+LABS,FULL]');s=s.replace('range(4)for j','range(5)for j');s=s.replace("out=[];names=[]","if fit:self.labs={v:SplineTransformer(n_knots=3,degree=3,include_bias=False,extrapolation='linear').fit(x[[v]])for v in LABS if v in x}\n  out=[];names=[]");s=s.replace("elif v=='bmi':","elif v in LABS:\n    z=self.labs[v].transform(x[[v]]);out.extend(z.T);names.extend(v+'_spline'+str(j)for j in range(z.shape[1]))\n   elif v=='bmi':");s=s.replace('no_external_update=True)',"lab_bsplines={v:dict(t=s.bsplines_[0].t.tolist(),c=s.bsplines_[0].c.tolist(),k=s.bsplines_[0].k)for v,s in self.labs.items()},no_external_update=True)");s=s.replace('panel=3,interaction=False','panel=4,interaction=False');s=s.replace('return ref',"ref['laboratories']={str(sex):{v:float(q.loc[q.male.eq(sex),v].median())for v in LABS}for sex in [0,1]}\n return ref");s=s.replace('return r\n',"for v in LABS:r[v]=spec['laboratories'][str(sex)][v]\n return r\n");(p/'core.py').write_text(s)
s=(v/'run.py').read_text();s=s.replace("src=P.parent.parent/'lung_age_study_20261018/shap_lung_age_v11/candidate_data_LOCAL_ONLY.csv'","src=P/'candidate_data_LOCAL_ONLY.csv'");(p/'run.py').write_text(s)
print(pd.DataFrame(qa).to_string(index=False))
