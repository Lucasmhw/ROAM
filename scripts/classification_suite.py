import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import numpy as np
import torch
from sklearn.model_selection import GroupShuffleSplit
from roam.classification import load_har,describe_classification
from roam.models import TemporalClassifier
from roam.controls import Controls,AffineInitializer
from roam.train import fit,population_fit
from run_suite import random_controls,save,code_hash


def main(args):
    torch.set_num_threads(4);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    data=load_har(args.data,args.device)
    save(out/'data.json',data['metadata'])
    if args.download_only:
        print('HAR_READY',data['metadata'],flush=True);return
    factory=lambda:TemporalClassifier(9,6)
    initializer_path=out/'initializer.json'
    if not initializer_path.exists():
        # Six training-only source tasks formed by disjoint-subject internal splits.
        # Neither target validation subjects nor test subjects are in these tasks.
        c_all=[];ctl_all=[];source_records=[]
        rng=np.random.default_rng(2042)
        candidates=[Controls.default(3)]+[random_controls(rng,3) for _ in range(7)]
        for task,(tr,va) in enumerate(GroupShuffleSplit(n_splits=6,test_size=.3,random_state=42).split(np.zeros(len(data['train_subjects'])),groups=data['train_subjects'])):
            path=out/f'source_{task}.json'
            if path.exists(): record=json.loads(path.read_text())
            else:
                source_x,source_y=data['train']
                local_mean=source_x[tr].mean((0,1));local_scale=source_x[tr].std((0,1),unbiased=False).clamp_min(1e-8)
                subset={**data,'train':((source_x[tr]-local_mean)/local_scale,source_y[tr]),'val':((source_x[va]-local_mean)/local_scale,source_y[va])}
                torch.manual_seed(2026);model=factory().to(args.device)
                c=describe_classification(model,subset,2026)
                runs=[]
                for i,control in enumerate(candidates):
                    r,_,_=fit(factory,subset,seed=2026,controls=control,steps=500,eval_every=100,classification=True,test=False)
                    runs.append(r); print('CLASS_SOURCE',task,i,r['val'],flush=True)
                best=int(np.argmin([r['val'] for r in runs]))
                record={'descriptor':c.tolist(),'selected_controls':candidates[best].to_dict(),'runs':runs,'source_train_subjects':np.unique(data['train_subjects'][tr]).tolist(),'source_validation_subjects':np.unique(data['train_subjects'][va]).tolist(),'source_normalization_mean_in_outer_units':local_mean.cpu().tolist(),'source_normalization_scale_in_outer_units':local_scale.cpu().tolist()}
                save(path,record)
            c_all.append(record['descriptor']);ctl_all.append(Controls(**record['selected_controls']));source_records.append(record)
        initializer=AffineInitializer.fit(c_all,ctl_all,provenance={'source_tasks':6,'source_tasks_within_target_training_subjects':True,'target_val_and_test_excluded':True,'source_seconds':sum(r['seconds'] for rec in source_records for r in rec['runs']),'classification_extension':'H/T=0; window-averaged statistics; cross-entropy Fisher'})
        initializer.save(initializer_path)
    initializer=AffineInitializer.load(initializer_path)
    tuning_path=out/'adamw_selection.json'
    if tuning_path.exists(): tuning=json.loads(tuning_path.read_text())
    else:
        runs=[]
        for lr in [1e-4,3e-4,1e-3,3e-3]:
            r,_,_=fit(factory,data,seed=2027,method='adamw',lr=lr,steps=1500,eval_every=300,classification=True,test=False)
            runs.append(r)
        tuning={'lr':min(runs,key=lambda r:r['val'])['lr'],'runs':runs};save(tuning_path,tuning)
    for seed in range(args.seeds):
        torch.manual_seed(seed);model=factory().to(args.device)
        c=describe_classification(model,data,seed);controls=initializer(c);controls.eval_interval=200
        for arm in ['conditioned','source_mean','direct_search','continuous_blend']:
            path=out/f'target_{arm}_seed{seed}.json'
            if path.exists(): continue
            control=Controls.from_latent(initializer.bias,3) if arm=='source_mean' else controls
            initial=None
            if arm=='direct_search':
                rng=np.random.default_rng(seed+99000)
                initial=[Controls.default(3)]+[random_controls(rng,3) for _ in range(3)]
            r,state=population_fit(factory,data,seed,control,steps=100000,wall_seconds=args.seconds,rounds=5,initial_controls=initial,classification=True,switching='blend' if arm=='continuous_blend' else 'discrete',test=True)
            r.update({'dataset':'UCI-HAR','arm':arm,'backbone':'TemporalCNN','descriptor':c.tolist(),'data':data['metadata'],'code_sha256':code_hash(),'initial_control_candidates':[item.to_dict() for item in initial] if initial else None})
            checkpoint=out/'checkpoints'/path.with_suffix('.pt').name;checkpoint.parent.mkdir(exist_ok=True);torch.save(state,checkpoint)
            save(path,r);print('CLASS_TARGET',seed,arm,r['test'],flush=True)
        path=out/f'target_adamw_seed{seed}.json'
        if not path.exists():
            r,state,_=fit(factory,data,seed=seed,method='adamw',lr=tuning['lr'],steps=1500,eval_every=300,classification=True,test=True)
            r.update({'dataset':'UCI-HAR','arm':'adamw','backbone':'TemporalCNN','data':data['metadata'],'budget_note':'1500 updates; costs recorded; not wall-clock matched to population runs'})
            checkpoint=out/'checkpoints'/path.with_suffix('.pt').name;checkpoint.parent.mkdir(exist_ok=True);torch.save(state,checkpoint)
            save(path,r);print('CLASS_TARGET',seed,'adamw',r['test'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/classification');p.add_argument('--data',default='data');p.add_argument('--device',default='cuda');p.add_argument('--seeds',type=int,default=10);p.add_argument('--seconds',type=float,default=30);p.add_argument('--download-only',action='store_true');main(p.parse_args())
