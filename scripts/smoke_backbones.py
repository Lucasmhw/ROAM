import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import torch
from roam.backbones import make_backbone
from roam.optimizer import ROAMOptimizer

p=argparse.ArgumentParser();p.add_argument('--model',choices=['DLinear','iTransformer','PatchTST','TimeMixer','ModernTCN'],required=True);a=p.parse_args()
torch.set_num_threads(2);torch.manual_seed(1)
model=make_backbone(a.model,96,96,7)
batch=(torch.randn(4,96,7),torch.randn(4,96,7))
out=model(batch[0]);assert out.shape==batch[1].shape
optimizer=ROAMOptimizer(model,refresh=10,check_every=1)
for _ in range(4):result=optimizer.step(batch,(batch,batch))
assert torch.isfinite(model(batch[0])).all()
print(json.dumps({'model':a.model,'output_shape':list(out.shape),'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),'blocks':len(optimizer.blocks),'metric_min':optimizer.G.min().item(),'counts':optimizer.counts}))
