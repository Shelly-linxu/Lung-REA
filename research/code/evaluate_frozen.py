"""Apply the released model and describe five-year calibration without updating.

Inputs must already have verified five-year binary outcome e5 and engineered
predictors. This utility does not resolve censoring or estimate survey-design CIs.
"""
from pathlib import Path
import argparse,json,sys
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'scoring'))
sys.path.insert(0,str(P/'NHANES_stability_v20'))
from predict_lung_rea import predict
from direct_core import metrics

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('input_csv');a.add_argument('output_directory');args=a.parse_args()
 x=pd.read_csv(args.input_csv)
 if 'e5'not in x or x.e5.isna().any()or not x.e5.isin([0,1]).all():raise ValueError('A verified nonmissing binary e5 outcome is required')
 if x.e5.nunique()!=2:raise ValueError('Both outcome classes are required for AUROC/calibration diagnostics')
 pred=predict(x);o=Path(args.output_directory);o.mkdir(parents=True,exist_ok=True)
 report=metrics(x.e5,pred.risk_5y);report.update({'parameter_updating':False,'confidence_intervals':'Only descriptive Wilson intervals for decile observed mortality; no survey or model-selection uncertainty.'})
 (o/'aggregate_performance.json').write_text(json.dumps(report,indent=2))
 result=pred.copy();result.insert(0,'row_number',np.arange(len(x)));result.to_csv(o/'predictions_LOCAL_ONLY.csv',index=False)
 groups=pd.qcut(pred.risk_5y,q=10,labels=False,duplicates='drop');rows=[]
 for dec in sorted(groups.dropna().unique()):
  ix=groups.eq(dec);n=int(ix.sum());e=int(x.loc[ix,'e5'].sum());ph=e/n;den=1+1.96**2/n;ctr=(ph+1.96**2/(2*n))/den;half=1.96*np.sqrt(ph*(1-ph)/n+1.96**2/(4*n*n))/den
  rows.append(dict(decile=int(dec)+1,n=n,deaths=e,predicted=float(pred.loc[ix,'risk_5y'].mean()),observed=ph,observed_low=ctr-half,observed_high=ctr+half))
 pd.DataFrame(rows).to_csv(o/'aggregate_calibration_deciles.csv',index=False)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
