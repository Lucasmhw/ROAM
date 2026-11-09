"""Charge source calibration to conditioned initialization on a first task.

The descriptor-free competitor receives at most the same calibration elapsed
time and number of validation calls, followed by the same target population
budget. It chooses controls using the target validation split only.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import time
import numpy as np
import torch
from roam.models import DLinear
from roam.data import forecast_data
from roam.controls import Controls
from roam.train import fit,population_fit
from run_suite import save,random_controls,code_hash


def main(a):
    torch.set_num_threads(4)
    out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    cal=json.loads((Path(a.suite)/'calibration_summary.json').read_text())
    cap=cal['total_source_seconds'];max_trials=cal['validation_calls']//5
    for name in ['ETTh2','ETTm2']:
        data=forecast_data(name,96,96,a.data,a.device)
        factory=lambda:DLinear(96,96,7)
        for seed in range(a.seeds):
            path=out/f'{name}_seed{seed}.json'
            if path.exists():continue
            rng=np.random.default_rng(seed+71000)
            candidates=[];consumed=0.;winner=None;best=float('inf')
            for trial in range(max_trials):
                # Keep a conservative allowance for a complete 1000-step trial.
                if trial and consumed+max(r['seconds'] for r in candidates)>cap:break
                control=Controls.default(2) if trial==0 else random_controls(rng)
                r,_,_=fit(factory,data,seed=seed,controls=control,steps=1000,eval_every=200,test=False)
                consumed+=r['seconds'];candidates.append(r)
                if r['val']<best:best=r['val'];winner=control
                print('COLD_SEARCH',name,seed,trial,r['val'],consumed,flush=True)
            final,state=population_fit(factory,data,seed,winner,steps=100000,wall_seconds=a.seconds,rounds=5,test=True)
            final.update({'dataset':name,'backbone':'DLinear','horizon':96,'arm':'direct_search_with_calibration_budget','source_calibration_seconds_cap':cap,'source_calibration_validation_calls_cap':cal['validation_calls'],'target_search_seconds':consumed,'target_search_validation_calls':sum(r['validation_calls'] for r in candidates),'target_search_trials':len(candidates),'target_search_runs':candidates,'total_measured_training_seconds':consumed+final['seconds'],'code_sha256':code_hash()})
            checkpoint=out/'checkpoints'/path.with_suffix('.pt').name;checkpoint.parent.mkdir(exist_ok=True);torch.save(state,checkpoint)
            save(path,final);print('COLD_DONE',name,seed,final['test'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite',default='results/suite');p.add_argument('--out',default='results/coldstart');p.add_argument('--data',default='data');p.add_argument('--device',default='cuda');p.add_argument('--seeds',type=int,default=3);p.add_argument('--seconds',type=float,default=20);main(p.parse_args())
