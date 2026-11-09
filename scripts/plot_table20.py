"""Regenerate Figure 6 from explicit Table 20 records, indexed by labels."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def save(fig,path):
    fig.savefig(path.with_suffix('.png'),dpi=250,bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight',metadata={'Creator':'ROAM plotting script','CreationDate':None})
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight',metadata={'Date':None})
    plt.close(fig)


def main(a):
    source=json.loads(Path(a.input).read_text());out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    rows=source['pairs'];sources=['ETTh1','ETTm1','Weather','ECL'];targets=['ETTh2','Weather','ECL','Exchange']
    grid=np.full((len(sources),len(targets)),np.nan);lookup={}
    for row in rows:
        key=(row['source'],row['target']);assert key not in lookup
        gain=100*(row['standard_mse']-row['roam_mse'])/row['standard_mse']
        lookup[key]=gain;grid[sources.index(key[0]),targets.index(key[1])]=gain
    assert [round(lookup[k],1) for k in [('ETTh1','ETTh2'),('ETTm1','Weather'),('Weather','ECL'),('ECL','Exchange')]]==[6.9,5.2,6.0,5.4]
    plt.rcParams.update({'font.size':11,'pdf.fonttype':42,'svg.fonttype':'none'})
    cmap=plt.get_cmap('Blues').copy();cmap.set_bad('#edf0f4')
    fig,ax=plt.subplots(figsize=(7.1,5.7));im=ax.imshow(np.ma.masked_invalid(grid),cmap=cmap,vmin=0,vmax=7)
    ax.set_xticks(range(4),targets);ax.set_yticks(range(4),sources);ax.set_xlabel('Target dataset');ax.set_ylabel('Source dataset')
    ax.set_title('Relative MSE reduction for the pairs in Table 20',pad=15,fontsize=12)
    ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,4,1),minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',bottom=False,left=False)
    for i in range(4):
        for j in range(4):
            value=grid[i,j];ax.text(j,i,'--' if np.isnan(value) else f'{value:.1f}%',ha='center',va='center',fontsize=13,color='#617080' if np.isnan(value) else 'white',fontweight='normal' if np.isnan(value) else 'bold')
    cbar=fig.colorbar(im,ax=ax,fraction=.047,pad=.04);cbar.set_label('Relative MSE reduction (%)')
    ax.legend(handles=[Patch(facecolor='#edf0f4',edgecolor='#b9c0c9',label='Pair not individually reported in Table 20')],loc='upper center',bbox_to_anchor=(.5,-.18),frameon=False,fontsize=9)
    fig.tight_layout();save(fig,out/'Figure6_Table20_consistent')
    fig,ax=plt.subplots(figsize=(7.7,4.5));x=np.arange(len(rows));width=.34
    b1=ax.bar(x-width/2,[r['standard_mse'] for r in rows],width,label='Standard recipe',color='#9aa9b8')
    b2=ax.bar(x+width/2,[r['roam_mse'] for r in rows],width,label='ROAM',color='#1768a6')
    ax.bar_label(b1,fmt='%.3f',padding=3,fontsize=9);ax.bar_label(b2,fmt='%.3f',padding=3,fontsize=9)
    ax.set_xticks(x,[r['source']+' → '+r['target'] for r in rows],rotation=10);ax.set_ylabel('Reported test MSE');ax.set_ylim(0,.55);ax.set_title('Source-target results reported in Table 20',fontsize=12)
    ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.15)
    fig.tight_layout();save(fig,out/'Table20_pairwise_MSE')
    with (out/'Figure6_data.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=['source','target','standard_mse','roam_mse','gain_percent']);writer.writeheader()
        for row in rows:writer.writerow({k:row[k] for k in ['source','target','standard_mse','roam_mse']}|{'gain_percent':lookup[(row['source'],row['target'])]})
    (out/'Figure6_provenance.json').write_text(json.dumps({'input':a.input,'provenance':source['provenance'],'formula':'100 * (standard_mse - roam_mse) / standard_mse','label_keyed_values':{s+' -> '+t:v for (s,t),v in lookup.items()},'unlisted_pairs':'masked, not zero','scope':source['figure_scope'],'matplotlib_version':matplotlib.__version__,'numpy_version':np.__version__},indent=2))
    print('Generated',out/'Figure6_Table20_consistent.png')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default='docs/table20_reported_values.json');p.add_argument('--out',default='results/figures');main(p.parse_args())
