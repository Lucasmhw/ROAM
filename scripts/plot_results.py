"""Publication-oriented figures generated from the same JSON run ledger."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def records(folder,pattern):return [json.loads(p.read_text()) for p in sorted(folder.glob(pattern))]
def save(fig,path):
    fig.savefig(path.with_suffix('.png'),dpi=200,bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight',metadata={'Creator':'ROAM experiment scripts','CreationDate':None})
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight',metadata={'Date':None})
    plt.close(fig)


def main(a):
    root=Path(a.root);out=root/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    arms=['conditioned','source_mean','direct_search'];labels=['Conditioned','Source mean','Direct search'];colors=['#1967a3','#b66022','#64748b','#8b5aa5','#268571']
    fig,axes=plt.subplots(1,2,figsize=(9,3.7))
    for ax,dataset in zip(axes,['ETTh2','ETTm2']):
        for x,(arm,label,color) in enumerate(zip(arms,labels,colors)):
            data=records(root/'suite',f'target_{dataset}_96_{arm}_seed*.json');assert len(data)==10
            values=np.array([r['test']['mse'] for r in data]);jitter=np.linspace(-.11,.11,len(values))
            ax.scatter(x+jitter,values,s=15,alpha=.55,c=color)
            ax.errorbar(x,values.mean(),yerr=values.std(ddof=1),fmt='D',ms=6,capsize=5,color=color)
        ax.set_xticks(range(3),labels,rotation=13);ax.set_title(dataset+', context/horizon 96/96');ax.set_ylabel('Test MSE');ax.grid(axis='y',alpha=.18)
    fig.suptitle('Source-fitted optimizer controls transferred to held-out datasets',fontsize=12)
    fig.text(.5,-.02,'Ten seeds; points are individual runs, diamonds are means, bars are sample SD.\nFour members, 20 s target training/validation, 20 validation calls. Source calibration is additional.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,1));save(fig,out/'control_transfer')
    fig,axes=plt.subplots(2,2,figsize=(9,6.8))
    policies=['conditioned','continuous_blend','phase_i_only'];names=['Discrete','Continuous blend','Phase I only']
    for column,(ax,dataset) in enumerate(zip(axes[0],['ETTh2','ETTm2'])):
        for x,(arm,label,color) in enumerate(zip(policies,names,colors)):
            data=records(root/'suite',f'target_{dataset}_96_{arm}_seed*.json');assert len(data)==10
            values=np.array([r['test']['mse'] for r in data]);ax.scatter(x+np.linspace(-.11,.11,10),values,s=15,alpha=.55,c=color);ax.errorbar(x,values.mean(),yerr=values.std(ddof=1),fmt='D',ms=6,capsize=5,color=color)
            progress=np.array([[min(item['val']['loss'] for item in r['history'][:4*round_id]) for round_id in range(1,6)] for r in data])
            lower=axes[1,column];mean=progress.mean(0);sd=progress.std(0,ddof=1)
            lower.plot(range(1,6),mean,marker='o',ms=3,color=color,label=label)
            lower.fill_between(range(1,6),mean-sd,mean+sd,color=color,alpha=.12)
        ax.set_xticks(range(3),names,rotation=13);ax.set_title(dataset);ax.set_ylabel('Test MSE');ax.grid(axis='y',alpha=.18)
        lower.set_xticks(range(1,6));lower.set_xlabel('Population validation round');lower.set_ylabel('Best-so-far validation MSE');lower.grid(alpha=.18)
    axes[1,0].legend(frameon=False,fontsize=8)
    fig.suptitle('Phase policy comparison under the same target budget',fontsize=12)
    fig.text(.5,-.02,'Same task initializer and metric; four members, 20 s, five evaluation rounds.\nTop: test MSE. Bottom: validation selection progress. Mean ± sample SD over ten seeds.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));save(fig,out/'phase_policy')
    if a.forecast_only:
        print('Generated forecasting figures in',out);return
    if not a.convex_only:
        fig,ax=plt.subplots(figsize=(7.8,3.8))
        class_arms=['conditioned','source_mean','direct_search','continuous_blend','adamw'];class_names=['Conditioned','Source mean','Direct search','Continuous blend','AdamW (1500 steps)']
        for x,arm in enumerate(class_arms):
            data=records(root/'classification',f'target_{arm}_seed*.json');assert len(data)==10
            values=np.array([100*r['test']['accuracy'] for r in data]);color=colors[x%len(colors)]
            ax.scatter(x+np.linspace(-.12,.12,10),values,s=15,alpha=.55,c=color);ax.errorbar(x,values.mean(),yerr=values.std(ddof=1),fmt='D',ms=6,capsize=5,color=color)
        ax.set_xticks(range(5),class_names,rotation=12);ax.set_ylabel('Test accuracy (%)');ax.set_title('UCI HAR, held-out test subjects');ax.grid(axis='y',alpha=.18)
        fig.text(.5,-.04,'Population arms: 30 s and 20 validation calls. AdamW has a separate update budget.\nPoints: ten seeds; diamond and bars: mean ± sample SD.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.08,1,1));save(fig,out/'classification')
    fig,axes=plt.subplots(1,2,figsize=(9,3.8))
    for ax,dataset in zip(axes,['ETTh2','ETTm2']):
        for arm,label,color,folder,pattern in [
            ('adamw_zero_extended','AdamW, zero decay',colors[1],root/'convex_zero',f'{dataset}_96_adamw_zero_extended_seed*.json'),
            ('roam_zero_tuned','ROAM, zero decay',colors[0],root/'convex_zero',f'{dataset}_96_roam_zero_tuned_seed*.json')]:
            data=records(folder,pattern);assert len(data)==10
            steps=np.array([h['step'] for h in data[0]['history']]);values=np.array([[h['val']['mse'] for h in r['history']] for r in data]);mean=values.mean(0);sd=values.std(0,ddof=1)
            ax.plot(steps,mean,color=color,label=label);ax.fill_between(steps,mean-sd,mean+sd,color=color,alpha=.16)
        exact=json.loads((root/'exact'/f'{dataset}_96.json').read_text());ax.axhline(exact['val']['mse'],color=colors[2],ls='--',label='Exact least squares')
        ax.set_xscale('log');ax.set_xticks([200,1000,2000,10000],['200','1k','2k','10k']);ax.set_xlabel('Training updates (log scale)');ax.set_ylabel('Validation MSE');ax.set_title(dataset+', horizon 96');ax.grid(alpha=.16)
    axes[0].legend(frameon=False,fontsize=8)
    fig.suptitle('DLinear validation trajectories on the same unregularized objective',fontsize=12)
    fig.text(.5,-.02,'Mean ± sample SD over ten seeds. The exact solution minimizes training MSE; the dashed line shows its validation MSE.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save(fig,out/'dlinear_validation_trajectories')
    fig,axes=plt.subplots(2,3,figsize=(10,6.2));tasks=[('ETTh2',96),('ETTh2',192),('ETTh2',336),('ETTh2',720),('ETTm2',96)]
    for ax,(dataset,horizon) in zip(axes.flat,tasks):
        for x,(arm,color) in enumerate(zip(['adamw_zero','adamw_zero_extended','roam_zero_tuned'],[colors[1],colors[2],colors[0]])):
            folder=root/'convex_zero';prefix=''
            data=records(folder,f'{prefix}{dataset}_{horizon}_{arm}_seed*.json');assert len(data)==10
            values=np.array([r['final_train']['mse'] for r in data]);ax.errorbar(x,values.mean(),yerr=values.std(ddof=1),fmt='o',color=color,capsize=4)
        exact=json.loads((root/'exact'/f'{dataset}_{horizon}.json').read_text());ax.axhline(exact['train']['mse'],ls='--',color='#222222',lw=1)
        ax.set_xticks([0,1,2],['AdamW 2k','AdamW 10k','ROAM 2k'],rotation=13,fontsize=8);ax.set_title(f'{dataset}, H={horizon}',fontsize=10);ax.set_ylabel('Final training MSE');ax.grid(axis='y',alpha=.16)
    axes.flat[-1].axis('off');axes.flat[-1].text(.03,.8,'Same objective: weight decay = 0\n\nPoints: mean over 10 seeds\nBars: sample standard deviation\nDashed: exact least-squares minimum\n\nFinal training loss is distinct from\nvalidation-selected test performance.',va='top',fontsize=10,linespacing=1.6)
    fig.suptitle('DLinear training objective versus the exact optimum',fontsize=12);fig.tight_layout();save(fig,out/'dlinear_training_objective')
    print('Generated figures in',out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='results')
    group=p.add_mutually_exclusive_group();group.add_argument('--forecast-only',action='store_true');group.add_argument('--convex-only',action='store_true')
    main(p.parse_args())
