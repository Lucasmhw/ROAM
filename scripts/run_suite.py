"""Rebuttal experiment manifest. Test results are never used for selection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import copy
import hashlib
import json
import platform
import time
import numpy as np
import torch
from roam.data import forecast_data,evaluate
from roam.models import DLinear
from roam.controls import Controls,AffineInitializer
from roam.train import fit,describe,population_fit


def save(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)); tmp.replace(path)


def random_controls(rng,blocks=2):
    return Controls(np.exp(rng.uniform(np.log(.1),np.log(10),blocks)).tolist(),
                    np.exp(rng.uniform(np.log(1e-5),np.log(.03),blocks)).tolist(),
                    rng.uniform(.05,.95,blocks).tolist(),float(rng.choice([.5,2.,5.])),
                    float(rng.choice([1e-4,1e-3,.01])),.2,200)


def code_hash():
    digest=hashlib.sha256()
    for p in sorted(Path('roam').glob('*.py')):
        digest.update(p.name.encode()); digest.update(p.read_bytes())
    return digest.hexdigest()


def calibrate(args):
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    tasks=[(d,h) for d in ['ETTh1','ETTm1'] for h in [96,192,336,720]]
    rng=np.random.default_rng(20261107)
    candidates=[Controls.default(2)]+[random_controls(rng) for _ in range(args.candidates-1)]
    descriptors=[]; selected=[]; records=[]
    for name,horizon in tasks:
        path=out/f'calibration_{name}_{horizon}.json'
        if path.exists():
            record=json.loads(path.read_text())
        else:
            data=forecast_data(name,96,horizon,root=args.data,device=args.device)
            factory=lambda:DLinear(96,horizon,7)
            torch.manual_seed(2026); model=factory().to(args.device)
            descriptor=describe(model,data,2026)
            all_runs=[]
            for i,ctl in enumerate(candidates):
                r,_,_=fit(factory,data,seed=2026,controls=ctl,steps=args.calibration_steps,eval_every=200,test=False)
                all_runs.append(r)
                print('CALIBRATION',name,horizon,i,round(r['val'],7),flush=True)
            winner=int(np.argmin([r['val'] for r in all_runs]))
            record={'dataset':name,'horizon':horizon,'descriptor':descriptor.tolist(),'winner':winner,'selected_controls':candidates[winner].to_dict(),'runs':all_runs,'data':data['metadata'],'code_sha256':code_hash()}
            save(path,record)
            del data,model
            torch.cuda.empty_cache()
        descriptors.append(record['descriptor']); selected.append(Controls(**record['selected_controls'])); records.append(record)
    provenance={'source_tasks':tasks,'source_seed':2026,'fit':'ridge on validation-selected latent controls','ridge':1.,'candidates':args.candidates,'steps_per_candidate':args.calibration_steps,'target_datasets_excluded':['ETTh2','ETTm2'],'total_source_seconds':sum(r['seconds'] for record in records for r in record['runs']),'validation_calls':sum(r['validation_calls'] for record in records for r in record['runs']),'code_sha256':code_hash()}
    initializer=AffineInitializer.fit(descriptors,selected,ridge=1.,provenance=provenance)
    initializer.save(out/'initializer.json')
    save(out/'calibration_summary.json',provenance)
    print('CALIBRATION_DONE',provenance,flush=True)


def target_experiments(args):
    out=Path(args.out); initializer=AffineInitializer.load(out/'initializer.json')
    for name in ['ETTh2','ETTm2']:
        data=forecast_data(name,96,96,root=args.data,device=args.device)
        factory=lambda:DLinear(96,96,7)
        for seed in range(args.seeds):
            torch.manual_seed(seed); model=factory().to(args.device)
            descriptor=describe(model,data,seed)
            conditioned=initializer(descriptor)
            conditioned.eval_interval=200
            average=Controls.from_latent(initializer.bias,2); average.eval_interval=200
            for arm in ['conditioned','source_mean','direct_search','continuous_blend','phase_i_only','identity']:
                path=out/f'target_{name}_96_{arm}_seed{seed}.json'
                if path.exists(): continue
                controls=average if arm=='source_mean' else conditioned
                initial=None
                if arm=='direct_search':
                    rng=np.random.default_rng(seed+99000)
                    initial=[Controls.default(2)]+[random_controls(rng) for _ in range(3)]
                switching='blend' if arm=='continuous_blend' else ('none' if arm=='phase_i_only' else 'discrete')
                r,state=population_fit(factory,data,seed,controls,steps=100000,wall_seconds=args.target_seconds,rounds=5,initial_controls=initial,switching=switching,metric=arm!='identity',test=True)
                r.update({'dataset':name,'horizon':96,'context':96,'backbone':'DLinear','arm':arm,'descriptor':descriptor.tolist(),'data':data['metadata'],'code_sha256':code_hash(),'initial_control_candidates':[c.to_dict() for c in initial] if initial else None})
                save(path,r)
                checkpoint=out/'checkpoints'/path.with_suffix('.pt').name; checkpoint.parent.mkdir(exist_ok=True)
                torch.save(state,checkpoint)
                print('TARGET',name,seed,arm,round(r['test']['mse'],7),round(r['seconds'],3),r['steps_per_member'],flush=True)
        del data; torch.cuda.empty_cache()


def baseline_experiments(args):
    out=Path(args.out); initializer=AffineInitializer.load(out/'initializer.json')
    for name,horizon in [('ETTh2',96),('ETTh2',192),('ETTh2',336),('ETTh2',720),('ETTm2',96)]:
        data=forecast_data(name,96,horizon,root=args.data,device=args.device)
        factory=lambda:DLinear(96,horizon,7)
        tuning_path=out/f'baseline_selection_{name}_{horizon}.json'
        if tuning_path.exists():
            tuning=json.loads(tuning_path.read_text())
        else:
            candidates=[]
            for lr in [1e-4,3e-4,1e-3,3e-3,1e-2]:
                for wd in [0.,1e-4,1e-3]:
                    r,_,_=fit(factory,data,seed=2027,method='adamw',lr=lr,weight_decay=wd,steps=2000,eval_every=200,test=False)
                    candidates.append(r)
            winner=min(candidates,key=lambda x:x['val'])
            tuning={'candidates':candidates,'lr':winner['lr'],'weight_decay':winner['weight_decay'],'selection_seed':2027}
            save(tuning_path,tuning)
        for seed in range(args.seeds):
            for arm,method,steps in [('adamw_tuned','adamw',2000),('adamw_extended','adamw',10000),('roam_single','roam',2000)]:
                path=out/f'convex_{name}_{horizon}_{arm}_seed{seed}.json'
                if path.exists(): continue
                torch.manual_seed(seed); model=factory().to(args.device)
                controls=initializer(describe(model,data,seed))
                r,state,last=fit(factory,data,seed=seed,method=method,controls=controls,lr=tuning['lr'] if method=='adamw' else .001,weight_decay=tuning['weight_decay'] if method=='adamw' else 0.,steps=steps,eval_every=200,test=True)
                r.update({'dataset':name,'horizon':horizon,'context':96,'backbone':'DLinear','arm':arm,'data':data['metadata'],'code_sha256':code_hash()})
                save(path,r)
                print('CONVEX',name,horizon,seed,arm,round(r['test']['mse'],7),round(r['final_train']['mse'],7),flush=True)
        del data; torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['calibrate','targets','baselines','all'],default='all')
    p.add_argument('--out',default='results/suite'); p.add_argument('--data',default='data')
    p.add_argument('--device',default='cuda'); p.add_argument('--seeds',type=int,default=10)
    p.add_argument('--candidates',type=int,default=16); p.add_argument('--calibration-steps',type=int,default=1000)
    p.add_argument('--target-seconds',type=float,default=20.)
    args=p.parse_args(); torch.set_num_threads(4)
    Path(args.out).mkdir(parents=True,exist_ok=True)
    try:
        import fcntl
        run_lock=open(Path(args.out)/'run.lock','w')
        fcntl.flock(run_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except ImportError:
        pass
    except BlockingIOError:
        print('SUITE_ALREADY_RUNNING',flush=True);sys.exit(0)
    save(Path(args.out)/'environment.json',{'python':platform.python_version(),'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'args':vars(args),'code_sha256':code_hash()})
    if args.stage in ['calibrate','all']: calibrate(args)
    if args.stage in ['targets','all']: target_experiments(args)
    if args.stage in ['baselines','all']: baseline_experiments(args)
