import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import torch
from roam.data import forecast_data,sample_batch
from roam.descriptors import trajectory_descriptors
from roam.backbones import make_backbone
from roam.controls import Controls,AffineInitializer
from roam.models import module_blocks
from roam.train import fit

p=argparse.ArgumentParser()
p.add_argument('--model',choices=['DLinear','iTransformer','PatchTST','TimeMixer','ModernTCN'],default='DLinear')
p.add_argument('--dataset',default='ETTh2');p.add_argument('--horizon',type=int,default=96);p.add_argument('--context',type=int,default=96)
p.add_argument('--steps',type=int,default=2000);p.add_argument('--seed',type=int,default=0);p.add_argument('--lr',type=float,default=.001)
p.add_argument('--method',choices=['adamw','roam'],default='roam');p.add_argument('--data',default='data');p.add_argument('--output',default='results/manual.json');p.add_argument('--device',default='cuda')
p.add_argument('--initializer',help='JSON affine initializer compatible with this backbone block partition')
a=p.parse_args();torch.set_num_threads(4)
data=forecast_data(a.dataset,a.context,a.horizon,a.data,a.device)
factory=lambda:make_backbone(a.model,a.context,a.horizon,data['metadata']['channels'])
torch.manual_seed(a.seed);model=factory().to(a.device);controls=Controls.default(len(module_blocks(model)))
descriptor=None
if a.initializer:
    initializer=AffineInitializer.load(a.initializer)
    if initializer.blocks!=len(module_blocks(model)):raise ValueError('Initializer block count does not match this backbone')
    generator=torch.Generator(device=a.device).manual_seed(a.seed+50000)
    parameters=[p for p in model.parameters() if p.requires_grad];gradients=[]
    for _ in range(2):
        x,y=sample_batch(data['train'],64,generator)
        loss=torch.nn.functional.mse_loss(model(x),y)
        gradients.append(torch.cat([g.detach().flatten() for g in torch.autograd.grad(loss,parameters)]))
    h1,h2=gradients;gns=((h1-h2).square().sum()/(((h1+h2)/2).square().sum()+1e-8)).item()
    descriptor=trajectory_descriptors(data['trajectory'],a.horizon,a.context,gns)
    controls=initializer(descriptor)
r,state,last=fit(factory,data,a.seed,a.method,controls,lr=a.lr,steps=a.steps,test=True)
r['data']=data['metadata'];r['backbone']=a.model;r['initialization']='affine task initializer' if a.initializer else 'explicit task-independent default; fit an architecture-compatible initializer for task conditioning'
r['initializer_path']=a.initializer;r['descriptor']=descriptor.tolist() if descriptor is not None else None
Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(r,indent=2))
