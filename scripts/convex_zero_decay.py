"""Same unregularized quadratic control, independent of practical WD tuning."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import torch
from roam.models import DLinear
from roam.data import forecast_data
from roam.train import fit,describe
from roam.controls import AffineInitializer
from run_suite import save,code_hash


def main(a):
    torch.set_num_threads(4)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    initializer=AffineInitializer.load(Path(a.suite)/'initializer.json')
    for name,horizon in [('ETTh2',96),('ETTh2',192),('ETTh2',336),('ETTh2',720),('ETTm2',96)]:
        data=forecast_data(name,96,horizon,root=a.data,device=a.device)
        factory=lambda:DLinear(96,horizon,7)
        selection=json.loads((Path(a.suite)/f'baseline_selection_{name}_{horizon}.json').read_text())
        eligible=[r for r in selection['candidates'] if r['weight_decay']==0]
        chosen=min(eligible,key=lambda r:r['val'])
        save(out/f'selection_{name}_{horizon}.json',{'lr':chosen['lr'],'weight_decay':0.,'selection_seed':2027,'eligible_candidates':eligible,'note':'Existing zero-decay candidates; no test-based retuning.'})
        roam_selection_path=out/f'roam_selection_{name}_{horizon}.json'
        if roam_selection_path.exists():roam_selection=json.loads(roam_selection_path.read_text())
        else:
            torch.manual_seed(2027);model=factory().to(a.device)
            controls=initializer(describe(model,data,2027));runs=[]
            for lr in [1e-4,3e-4,1e-3,3e-3,1e-2]:
                r,_,_=fit(factory,data,seed=2027,method='roam',controls=controls,lr=lr,weight_decay=0.,steps=2000,eval_every=200,test=False)
                runs.append(r)
            roam_selection={'lr':min(runs,key=lambda r:r['val'])['lr'],'weight_decay':0.,'selection_seed':2027,'candidates':runs,'note':'Same five-LR validation grid as zero-decay AdamW; source initializer remains fixed.'}
            save(roam_selection_path,roam_selection)
        for seed in range(a.seeds):
            for arm,steps in [('adamw_zero',2000),('adamw_zero_extended',10000)]:
                path=out/f'{name}_{horizon}_{arm}_seed{seed}.json'
                if path.exists():continue
                if selection['weight_decay']==0 and selection['lr']==chosen['lr']:
                    original='adamw_tuned' if steps==2000 else 'adamw_extended'
                    source=Path(a.suite)/f'convex_{name}_{horizon}_{original}_seed{seed}.json'
                    r=json.loads(source.read_text());r['reused_from']=source.as_posix()
                else:
                    r,_,_=fit(factory,data,seed=seed,method='adamw',lr=chosen['lr'],weight_decay=0.,steps=steps,eval_every=200,test=True)
                r.update({'dataset':name,'horizon':horizon,'context':96,'backbone':'DLinear','arm':arm,'data':data['metadata'],'code_sha256':code_hash()})
                save(path,r)
                print('ZERO_DECAY',name,horizon,seed,arm,r['test']['mse'],r['final_train']['mse'],flush=True)
            path=out/f'{name}_{horizon}_roam_zero_tuned_seed{seed}.json'
            if not path.exists():
                if roam_selection['lr']==.001:
                    source=Path(a.suite)/f'convex_{name}_{horizon}_roam_single_seed{seed}.json'
                    r=json.loads(source.read_text());r['reused_from']=source.as_posix()
                else:
                    torch.manual_seed(seed);model=factory().to(a.device)
                    controls=initializer(describe(model,data,seed))
                    r,_,_=fit(factory,data,seed=seed,method='roam',controls=controls,lr=roam_selection['lr'],weight_decay=0.,steps=2000,eval_every=200,test=True)
                r.update({'dataset':name,'horizon':horizon,'context':96,'backbone':'DLinear','arm':'roam_zero_tuned','data':data['metadata'],'code_sha256':code_hash()});save(path,r)
                print('ZERO_DECAY',name,horizon,seed,'roam_zero_tuned',r['test']['mse'],r['final_train']['mse'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite',default='results/suite');p.add_argument('--out',default='results/convex_zero');p.add_argument('--data',default='data');p.add_argument('--device',default='cuda');p.add_argument('--seeds',type=int,default=10);main(p.parse_args())
