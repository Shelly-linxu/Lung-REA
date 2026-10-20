from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from PIL import Image
P=Path('lung_age_study_20261019/manuscript_lung_rea_v30');F=P/'figures'
fig,ax=plt.subplots(figsize=(12.8,8.0));ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1));blue='#296b91';orange='#b6793f'
def box(x,y,w,h,t,c,fs=10):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.006,rounding_size=0.007',edgecolor=c,facecolor='#f5f8fa',lw=1.1));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color='#203540',linespacing=1.3)
def arrow(x,y,xx,yy):ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=11,color='#74828b',lw=1))
ax.text(.245,.985,'A  Development population',ha='center',va='top',weight='bold',fontsize=12,color=blue);ax.text(.755,.985,'B  Historical evaluation population',ha='center',va='top',weight='bold',fontsize=12,color=orange)
left=[('NHANES 2007–2012 spirometry records: 23,433\nAge 50–79 retained: 7,330\nOutside age range: 16,103',.81,.13),('Plausible core measurements: 5,856\nExcluded for missing/implausible core: 1,474',.69,.09),('FEV₁ and FVC grades A/B; complete test: 4,925\nExcluded for spirometry quality: 931',.57,.09),('Harmonizable smoking status: 4,923\nExcluded for unknown smoking: 2',.45,.09),('Mortality linkage and final analysis: 4,915\nExcluded for unavailable eligible linkage/follow-up: 8\n243 deaths within five years; 4,672 non-events',.29,.13)]
right=[('NHANES III adult records: 20,050\nAge 50–79 retained: 6,822\nOutside age range: 13,228',.81,.13),('Plausible core measurements: 5,483\nExcluded for missing/implausible core: 1,339',.69,.09),('Reliable and reproducible MEC spirometry: 4,698\nExcluded for spirometry quality: 785',.57,.09),('Directly measured height: 4,634; excluded: 64\nKnown smoking and valid survey design: 4,634\nAdditional exclusions at these checks: 0',.43,.11),('Mortality linkage and final analysis: 4,633\nExcluded for unavailable eligible linkage/follow-up: 1\n434 deaths within five years; 4,199 non-events',.29,.11)]
for x,arr,c in [(.02,left,blue),(.53,right,orange)]:
 for i,(t,y,h)in enumerate(arr):
  box(x,y,.45,h,t,c)
  if i:prev=arr[i-1];arrow(x+.225,prev[1]-.006,x+.225,y+h+.006)
box(.02,.13,.27,.11,'Internal assessment\n3 repeats × 5 outer folds\n3-fold inner selection\nOOF predictions only',blue,9.5)
box(.33,.13,.31,.11,'Final development fit\n29 predictors; additive; C=0.003\nFit all 4,915; freeze preprocessing,\ncoefficients and age reference',blue,9.5)
box(.71,.13,.27,.11,'Apply the same frozen model\nNHANES III n=4,633\nNo fitting or risk updating\nHistorical evaluation only',orange,9.5)
arrow(.16,.284,.155,.246);arrow(.27,.284,.485,.246);arrow(.64,.185,.704,.185);arrow(.755,.284,.845,.246)
box(.02,.015,.62,.075,'All model selection and reference construction use development data\nDevelopment cycle n/deaths: 2007–2008 1,667/88; 2009–2010 1,735/81; 2011–2012 1,513/74',blue,9)
box(.71,.015,.27,.075,'Six-model comparison age 50–70\nDevelopment 3,960 / 147 deaths\nHistorical 3,506 / 230 deaths',orange,9)
fig.subplots_adjust(left=.005,right=.995,top=.995,bottom=.005)
for ext in ['png','svg']:fig.savefig(F/f'Figure1_development_and_evaluation.{ext}',dpi=320,facecolor='white',bbox_inches='tight')
Image.open(F/'Figure1_development_and_evaluation.png').convert('RGB').save(F/'Figure1_development_and_evaluation.tiff',compression='tiff_lzw',dpi=(320,320))
