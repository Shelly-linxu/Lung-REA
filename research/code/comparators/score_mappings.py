"""Score the study-fitted mortality mappings; published age equations remain fixed."""
import numpy as np
from scipy.interpolate import BSpline
from scipy.special import expit

def predict(d,lung_age,spec):
 z=np.asarray(lung_age).reshape(-1,1)
 if spec['adjusted']:z=np.column_stack([z,d.age.to_numpy()])
 basis=[]
 for j,t in enumerate(spec['spline_knots_by_feature']):
  t=np.asarray(t);degree=spec['spline_degree'];n=len(t)-degree-1;b=BSpline(t,np.eye(n),degree,extrapolate=False);x=z[:,j];lo=t[degree];hi=t[-degree-1];v=b(np.clip(x,lo,hi))
  below=x<lo;above=x>hi
  v[below]=b(lo)+(x[below]-lo)[:,None]*b.derivative()(lo)
  v[above]=b(hi)+(x[above]-hi)[:,None]*b.derivative()(hi)
  basis.append(v[:,:-1])
 a=np.column_stack(basis)
 if spec['adjusted']:a=np.column_stack([a,d.male.to_numpy()])
 a=(a-spec['scaler_mean'])/spec['scaler_scale'];return expit(spec['intercept']+a@np.asarray(spec['coef']))
