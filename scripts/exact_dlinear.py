"""Deterministic unregularized and ridge DLinear solutions in float64.

The effective forecast family is an unconstrained shared linear map of the
input. Solving in that identifiable coordinate system avoids a redundant
trend/seasonal parameterization. All targets/horizons are retained.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import argparse
import time
import numpy as np
import torch
from roam.data import forecast_data


def solve(data):
    start=time.perf_counter()
    x,y=data['train']; context=x.shape[1]; horizon=y.shape[1]
    # Pool channels as independent rows, with the same learned linear map.
    def features(pair):
        x,y=pair
        a=x.permute(0,2,1).reshape(-1,context).double()
        b=y.permute(0,2,1).reshape(-1,horizon).double()
        return torch.cat([a,torch.ones(len(a),1,dtype=a.dtype,device=a.device)],1),b
    A,Y=features(data['train'])
    gram=A.T@A/len(A); rhs=A.T@Y/len(A)
    values,vectors=torch.linalg.eigh(gram)
    tol=float(values.max())*1e-12
    weights=vectors@((vectors.T@rhs)/values.clamp_min(tol)[:,None])
    def metrics(w,pair):
        aa,yy=features(pair); err=aa@w-yy
        return {'mse':err.square().mean().item(),'mae':err.abs().mean().item()}
    residual=(gram@weights-rhs).norm().item()
    solution={'train':metrics(weights,data['train']),'val':metrics(weights,data['val']),'test':metrics(weights,data['test']),'normal_equation_residual':residual,'effective_design_rank':int((values>tol).sum()),'effective_design_columns':len(values),'positive_spectrum_condition':float(values.max()/values[values>tol].min()),'seconds':time.perf_counter()-start}
    candidates=[]; best=None; best_w=None
    penalty=torch.eye(len(gram),dtype=gram.dtype,device=gram.device); penalty[-1,-1]=0
    for ridge in [0.,1e-6,1e-5,1e-4,1e-3,.01,.1,1.,10.]:
        w=weights if ridge==0 else torch.linalg.solve(gram+ridge*penalty,rhs)
        val=metrics(w,data['val']); candidates.append({'ridge':ridge,'val':val})
        if best is None or val['mse']<best['val']['mse']:
            best=candidates[-1]; best_w=w
    solution['ridge_selection']={'candidates':candidates,'selected_ridge':best['ridge'],'train':metrics(best_w,data['train']),'val':best['val'],'test':metrics(best_w,data['test'])}
    return solution


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',default='results/exact');p.add_argument('--data',default='data');p.add_argument('--device',default='cpu');a=p.parse_args()
    torch.set_num_threads(4);Path(a.out).mkdir(parents=True,exist_ok=True)
    for name,horizon in [('ETTh2',96),('ETTh2',192),('ETTh2',336),('ETTh2',720),('ETTm2',96)]:
        path=Path(a.out)/f'{name}_{horizon}.json'
        if path.exists(): continue
        data=forecast_data(name,96,horizon,root=a.data,device=a.device)
        result=solve(data);result['data']=data['metadata']
        path.write_text(json.dumps(result,indent=2))
        print(name,horizon,json.dumps(result),flush=True)
