"""Six published FEV1 lung-age equations. Inputs: height m; fev L; male 0/1.
These equations are separate from the study-fitted mortality mappings.
"""
import numpy as np
import pandas as pd
def ages(d):
 h=d.height.to_numpy()*100;f=d.fev.to_numpy();m=d.male.to_numpy()==1;hi=h/2.54;hm=h/100
 a={}
 a['Morris']=np.where(m,2.870*hi-31.250*f-39.375,3.560*hi-40*f-77.280)
 a['Quanjer']=np.where(m,148.276*hm-85.8621-34.483*f,158*hm-104-40*f)
 # Exact algebraic inversion of published quadratic FEV1 coefficients; retain nonreal roots as missing.
 b=np.where(m,.01303,.00361);c=np.where(m,.000172,.000194);k=np.where(m,.5536,.4333)+np.where(m,.00014098,.00011496)*h*h
 disc=b*b+4*c*(k-f);a['Hankinson']=(-b+np.sqrt(np.maximum(disc,0)))/(2*c);a['Hankinson'][disc<0]=np.nan
 a['Gore']=np.where(m,(2.081+.5846*hm**3-f)/(.01599*hm),(1.597+.5552*hm**3-f)/(.01574*hm))
 b=np.where(m,.00183,.00422);c=np.where(m,.00011,.00015);k=np.where(m,-9.37674+2.10839*np.log(h),-8.49717+1.90019*np.log(h));disc=b*b+4*c*(k-np.log(f));a['Falaschetti']=(b+np.sqrt(np.maximum(disc,0)))/(2*c);a['Falaschetti'][disc<0]=np.nan
 a['Newbury']=np.where(m,-85.62+1.55563*h-33.69345*f,-74.65+1.32922*h-31.98025*f)
 return pd.DataFrame(a,index=d.index)

