import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import torch
from roam.data import forecast_data
from roam.models import DLinear
from roam.train import fit,describe,population_fit
from roam.controls import Controls

torch.set_num_threads(4)
data=forecast_data('ETTh2',96,96,device='cuda')
factory=lambda:DLinear(96,96,7)
model=factory().cuda()
print('descriptor',describe(model,data,0).tolist(),flush=True)
for method in ['adamw','roam']:
    r,_,_=fit(factory,data,method=method,steps=400,eval_every=100,test=False)
    print(json.dumps({k:v for k,v in r.items() if k!='history'}),flush=True)
r,_=population_fit(factory,data,0,Controls.default(2),steps=100000,wall_seconds=8,rounds=4,test=False)
print(json.dumps({k:v for k,v in r.items() if k!='history'}),flush=True)
