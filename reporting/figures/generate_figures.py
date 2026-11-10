"""Regenerate the manuscript figures from the reported numerical summaries.

Dependencies: matplotlib and numpy. Lines connect the supplied observations;
error bars are the reported seed standard deviations, not confidence intervals.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'figure_data.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,
    'axes.titlesize':8.5,'axes.labelsize':8,'legend.fontsize':7,
    'xtick.labelsize':7.5,'ytick.labelsize':7.5,
    'axes.spines.top':False,'axes.spines.right':False,
    'axes.grid':True,'grid.alpha':.17,'pdf.fonttype':42,
    'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
BLUE='#2769A2'; TEAL='#087D6C'; ORANGE='#BC6C15'; GRAY='#778592'; INK='#243746'
COL=[TEAL,BLUE,ORANGE,GRAY,'#8C678D']

def save(fig,name):
    for ext in ['png','pdf','svg']:
        fig.savefig(ROOT/f'{name}.{ext}',dpi=300,bbox_inches='tight',pad_inches=.035)
    plt.close(fig)

def figure6():
    a=D['transfer']; vals=100*(1-np.array(a['roam'])/np.array(a['baseline']))
    mat=np.full((4,4),np.nan);np.fill_diagonal(mat,vals)
    fig,ax=plt.subplots(figsize=(4.6,3.35),layout='constrained')
    cmap=plt.get_cmap('YlGnBu').copy();cmap.set_bad('#edf0f2')
    im=ax.imshow(np.ma.masked_invalid(mat),cmap=cmap,vmin=0,vmax=8)
    ax.grid(False);ax.set_xticks(range(4),a['targets']);ax.set_yticks(range(4),a['sources'])
    ax.set_xlabel('Target dataset');ax.set_ylabel('Source dataset')
    for i in range(4):
        for j in range(4):
            ax.text(j,i,f'{mat[i,j]:.2f}%' if i==j else 'NR',ha='center',va='center',fontsize=9,color='white' if i==j else '#778592')
    fig.colorbar(im,ax=ax,shrink=.87,label='Relative MSE reduction (%)')
    save(fig,'Figure6_Table20_consistent')

def figure8():
    a=D['descriptor']; vals=100*(np.array(a['mse'])/a['reference']-1)
    fig,ax=plt.subplots(figsize=(5.5,3.2),layout='constrained')
    y=np.arange(len(vals));ax.barh(y,vals,height=.62,color=[ORANGE if v>0 else TEAL for v in vals])
    ax.set_yticks(y,a['labels']);ax.invert_yaxis();ax.axvline(0,color=INK,lw=.7)
    for yi,v in zip(y,vals):ax.text(v+(.08 if v>=0 else -.08),yi,f'{v:+.2f}%',va='center',ha='left' if v>=0 else 'right',fontsize=7)
    ax.set_xlim(-1.65,6.25);ax.set_xlabel('MSE change versus six descriptors (%)')
    save(fig,'Figure8_Table15_consistent')

def workflow():
    fig,ax=plt.subplots(figsize=(5.5,2.82));fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99)
    ax.set_xlim(0,12);ax.set_ylim(0,6.3);ax.axis('off')
    def box(x,y,w,h,text,c):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.07,rounding_size=.08',facecolor=c,edgecolor='#a4b5c1',lw=.7))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=7.1,linespacing=1.4,color=INK)
    def ar(p,q):ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=8,color=GRAY,lw=.9))
    ax.text(.15,6.0,'SOURCE CALIBRATION',fontsize=7.8,weight='bold',color=BLUE)
    box(.15,4.62,3.45,1.08,'Training descriptors\nValidation-selected controls','#eaf2fa')
    box(4.28,4.62,3.4,1.08,'Standardize across tasks\nRidge fit of W and b','#eaf2fa')
    box(8.36,4.62,3.45,1.08,'Freeze coefficients\nand feature normalization','#eaf2fa')
    ar((3.68,5.16),(4.18,5.16));ar((7.76,5.16),(8.26,5.16))
    ax.axhline(4.17,color='#bfcbd3',ls='--',lw=.7)
    ax.text(.15,3.85,'TARGET TRAINING',fontsize=7.8,weight='bold',color=TEAL)
    box(.15,2.47,3.45,1.06,'Training statistics\n+ initial gradient disagreement','#e6f3ef')
    box(4.28,2.47,3.4,1.06,'Task controls\nScales, damping, mixtures, gates','#e6f3ef')
    box(8.36,2.47,3.45,1.06,'Realized metric\nControls + model derivatives','#e6f3ef')
    ar((3.68,3.0),(4.18,3.0));ar((7.76,3.0),(8.26,3.0));ar((10.05,4.53),(6.0,3.62))
    box(.15,.25,3.45,1.1,'Target validation\nPopulation + checkpoint selection','#fff0dc')
    box(4.28,.25,3.4,1.1,'Metric solve + phase policy\nOrdinary predictor weights','#e6f3ef')
    box(8.36,.25,3.45,1.1,'Current model + training batch\nPrediction Jacobian + gradient EMA','#eaf2fa')
    ar((10.05,1.45),(10.05,2.37));ar((8.4,2.38),(7.5,1.45))
    ar((4.18,.8),(3.7,.8));ar((7.78,.8),(8.26,.8));ar((3.5,1.42),(4.3,2.38))
    save(fig,'FigureR1_information_flow')

def points(ax,labels,means,sds,title,xlabel='Test MSE',annotate=False):
    for j,(m,s) in enumerate(zip(means,sds)):
        ax.errorbar(m,j,xerr=s,fmt='o',color=COL[j],capsize=2.4,ms=4,lw=1.15)
        if annotate:ax.annotate(f'{m:.3f}',(m,j),xytext=(0,6),textcoords='offset points',ha='center',fontsize=6.5,color=COL[j])
    ax.set_yticks(range(len(labels)),labels);ax.set_ylim(len(labels)-.5,-.7)
    ax.set_title(title);ax.set_xlabel(xlabel);ax.grid(axis='y',visible=False)

def control():
    a=D['control'];fig,axs=plt.subplots(1,3,figsize=(5.5,1.82),gridspec_kw={'width_ratios':[1,1,1.15]},layout='constrained')
    points(axs[0],['Conditioned','Source mean','Direct search'],a['ETTh2_mean'],a['ETTh2_sd'],'ETTh2-96',annotate=True)
    points(axs[1],['','',''],a['ETTm2_mean'],a['ETTm2_sd'],'ETTm2-96',annotate=True)
    ns=np.arange(1,101);axs[2].plot(ns,a['source_seconds']/ns+a['target_seconds'],color=TEAL,lw=1.5)
    for n in [1,10,100]:
        v=a['source_seconds']/n+a['target_seconds'];axs[2].scatter(n,v,s=12,c=TEAL)
        axs[2].annotate(f'{v:g}',(n,v),xytext=(3,3),textcoords='offset points',fontsize=7)
    axs[2].set(xscale='log',yscale='log',xlabel='Target tasks',ylabel='Seconds/task',title='Calibration + target',xlim=(.8,210),ylim=(18,1200))
    axs[2].set_xticks([1,10,100],['1','10','100'])
    save(fig,'FigureR2_control_and_cost')

def convex():
    a=D['convex'];fig,axs=plt.subplots(1,2,figsize=(5.5,2.0),layout='constrained')
    axs[0].plot(a['adamw_steps'],a['adamw_gap'],'o-',color=BLUE,label='AdamW',ms=3,lw=1.3)
    axs[0].plot(a['roam_steps'],a['roam_gap'],'o-',color=TEAL,label='ROAM',ms=3,lw=1.3)
    axs[0].set(yscale='log',xlabel='Updates',ylabel='Training MSE gap to exact LS',title='Same unregularized objective')
    axs[0].legend();axs[0].text(.98,.05,'Exact LS: gap = 0',transform=axs[0].transAxes,ha='right',fontsize=7,color=GRAY)
    axs[1].plot(a['adamw_steps'],a['adamw_val'],'o-',color=BLUE,label='AdamW',ms=3,lw=1.3)
    axs[1].plot(a['roam_steps'],a['roam_val'],'o-',color=TEAL,label='ROAM',ms=3,lw=1.3)
    axs[1].axhline(a['ls_val'],color=GRAY,ls='--',lw=1,label='Exact LS')
    axs[1].set(xlabel='Updates',ylabel='Validation MSE',title='Checkpoint-selection trajectory')
    axs[1].legend()
    save(fig,'FigureR3_dlinear_convergence')

def switching():
    a=D['switch'];fig,axs=plt.subplots(2,2,figsize=(5.5,3.65),layout='constrained')
    for j,ds in enumerate(['ETTh2','ETTm2']):
        points(axs[0,j],a['labels'] if j==0 else ['','',''],a[ds+'_mean'],a[ds+'_sd'],ds+'-96')
        for i,label in enumerate(a['labels']):axs[1,j].plot(a['rounds'],a[ds+'_val'][i],'o-',color=COL[i],label=label,ms=3,lw=1.2)
        axs[1,j].set(xlabel='Population evaluation round',ylabel='Best validation MSE',xticks=a['rounds'])
        axs[1,j].legend(fontsize=6.5)
    save(fig,'FigureR4_phase_policy')

def classification():
    a=D['classification'];fig,axs=plt.subplots(1,2,figsize=(5.5,2.22),layout='constrained')
    points(axs[0],a['labels'],a['accuracy'],a['accuracy_sd'],'UCI HAR accuracy','Test accuracy (%)')
    points(axs[1],['']*5,a['cross_entropy'],a['cross_entropy_sd'],'UCI HAR cross-entropy','Test cross-entropy')
    for ax in axs:ax.axhspan(3.5,4.5,color='#f3e5d4',alpha=.65,zorder=0)
    save(fig,'FigureR5_classification')

def curvature():
    a=D['curvature'];fig,axs=plt.subplots(1,2,figsize=(5.5,1.85),layout='constrained')
    for ax,ds in zip(axs,['ETTh2','ETTm2']):
        values=a[ds];bars=ax.bar(range(4),values,color=[GRAY,BLUE,ORANGE,TEAL],width=.62)
        ax.set_xticks(range(4),['Identity','Default','Source\nmean','Conditioned']);ax.set_ylim(0,max(values)*1.2)
        ax.set(title=ds+'-96',ylabel='Positive-spectrum condition ratio');ax.grid(axis='x',visible=False);ax.bar_label(bars,padding=3,fontsize=7)
    save(fig,'FigureR6_curvature_diagnostic')

def factorial():
    f={tuple(r[:3]):r[3] for r in D['factorial']['rows']}
    mat=np.array([[f[(m,s,o)] for o in [0,1]] for m,s in [(0,0),(0,1),(1,0),(1,1)]])
    gains=[np.mean([v-f[tuple(1 if j==i else q for j,q in enumerate(k))] for k,v in f.items() if k[i]==0]) for i in range(3)]
    fig,axs=plt.subplots(1,2,figsize=(5.5,2.1),layout='constrained',gridspec_kw={'width_ratios':[1,1.25]})
    axs[0].imshow(mat,cmap='YlGnBu_r',vmin=.310,vmax=.335,aspect='auto');axs[0].grid(False)
    axs[0].set_xticks([0,1],['O = 0','O = 1']);axs[0].set_yticks(range(4),['M=0, S=0','M=0, S=1','M=1, S=0','M=1, S=1']);axs[0].set_title('Complete factorial MSE')
    for i in range(4):
        for j in range(2):axs[0].text(j,i,f'{mat[i,j]:.3f}',ha='center',va='center',fontsize=8,color='white' if mat[i,j]<.320 else INK)
    axs[1].barh(range(3),gains,color=[TEAL,BLUE,ORANGE],height=.5);axs[1].set_yticks(range(3),['Metric','Switch','Outer']);axs[1].invert_yaxis()
    axs[1].set(xlim=(0,.0143),xlabel='Mean marginal MSE reduction',title='Four contrasts per component')
    for i,v in enumerate(gains):axs[1].text(v+.0002,i,f'{v:.5f}',va='center',fontsize=7)
    save(fig,'FigureR7_factorial')

if __name__=='__main__':
    for fn in [figure6,figure8,workflow,control,convex,switching,classification,curvature,factorial]:fn()
    print('Regenerated 9 numerical figures in PDF, PNG and SVG.')
