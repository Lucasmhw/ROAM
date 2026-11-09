"""Exact positive-spectrum diagnostic for DLinear at initialization.

The redundant model has flat directions. Report the nonzero spectrum of the
whitened full-training Hessian, without claiming that it is positive definite.
This is a training-only diagnostic; no optimizer or initializer is refitted.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import torch
from roam.models import DLinear,decompose
from roam.controls import Controls,AffineInitializer
from roam.optimizer import ROAMOptimizer
from roam.data import forecast_data,sample_batch
from roam.train import describe
from run_suite import save,code_hash


def compressed_design(data):
    x=data['train'][0].cpu();t=x.shape[1]
    a=x.permute(0,2,1).reshape(-1,t).double()
    a=torch.cat([a,torch.ones(len(a),1,dtype=torch.float64)],1)
    gram=a.T@a/len(a)
    eigenvalues,eigenvectors=torch.linalg.eigh(gram)
    assert eigenvalues.min()>0
    root=eigenvectors*eigenvalues.sqrt()[None,:]
    seasonal,trend=decompose(torch.eye(t,dtype=torch.float64).unsqueeze(-1))
    c=torch.zeros(t+1,2*t+2,dtype=torch.float64)
    c[:t,:t]=seasonal[:,:,0];c[-1,t]=1
    c[:t,t+1:2*t+1]=trend[:,:,0];c[-1,-1]=1
    return root.T@c,c.T@gram@c


def spectrum(metric,compressed,horizon,context,full_hessian=None):
    # Flattening order is seasonal.weight, seasonal.bias, trend.weight, trend.bias.
    weights=metric.cpu().double();block=horizon*(context+1)
    per_h=torch.cat([weights[:horizon*context].reshape(horizon,context),weights[horizon*context:block,None],weights[block:block+horizon*context].reshape(horizon,context),weights[block+horizon*context:,None]],1)
    reduced=(compressed[None,:,:]/per_h[:,None,:])@compressed.T
    values=torch.linalg.eigvalsh(reduced)*(2/horizon)
    assert values.min()>0
    if full_hessian is not None:
        invroot=per_h[0].rsqrt()
        full=invroot[:,None]*full_hessian*invroot[None,:]*(2/horizon)
        actual=torch.linalg.eigvalsh(full)[-(context+1):]
        assert torch.allclose(actual,values[0],rtol=1e-7,atol=1e-9)
    lo,hi=values.min().item(),values.max().item()
    return {'minimum_positive_eigenvalue':lo,'maximum_eigenvalue':hi,'positive_spectrum_condition':hi/lo,'positive_rank':horizon*(context+1),'nullity':horizon*(context+1),'per_output_condition':[float(v.max()/v.min()) for v in values]}


def main(a):
    torch.set_num_threads(4);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    initializer=AffineInitializer.load(Path(a.suite)/'initializer.json')
    for name in ['ETTh2','ETTm2']:
        data=forecast_data(name,96,96,root=a.data,device=a.device)
        compressed,full=compressed_design(data)
        for seed in range(a.seeds):
            path=out/f'{name}_seed{seed}.json'
            if path.exists():continue
            torch.manual_seed(seed);model=DLinear(96,96,7).to(a.device)
            c=describe(model,data,seed)
            generator=torch.Generator(device=a.device).manual_seed(seed+10000)
            batch=sample_batch(data['train'],64,generator)
            records={}
            for arm,control in [('conditioned',initializer(c)),('source_mean',Controls.from_latent(initializer.bias,2)),('default',Controls.default(2)),('identity',Controls.default(2))]:
                optimizer=ROAMOptimizer(model,control,metric=arm!='identity',seed=seed)
                optimizer.refresh_metric(batch)
                records[arm]=spectrum(optimizer.G,compressed,96,96,full if seed==0 else None)
                records[arm]['controls']=control.to_dict()
            save(path,{'dataset':name,'context':96,'horizon':96,'backbone':'DLinear','seed':seed,'descriptor':c.tolist(),'stage':'initial metric, D=0','hessian':'exact full-training unregularized MSE','arms':records,'data':data['metadata'],'code_sha256':code_hash()})
            print('CURVATURE',name,seed,{k:round(v['positive_spectrum_condition'],2) for k,v in records.items()},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--suite',default='results/suite');p.add_argument('--out',default='results/curvature');p.add_argument('--data',default='data');p.add_argument('--device',default='cuda');p.add_argument('--seeds',type=int,default=10);main(p.parse_args())
