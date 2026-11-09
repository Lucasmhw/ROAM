"""Pinned upstream backbone adapters (ordinary weights, deterministic dropout=0)."""
from pathlib import Path
from types import SimpleNamespace
import importlib
import sys
import torch
from torch import nn
from .models import DLinear,module_blocks

TSL_COMMIT='4e938a1767106324dd753b2a44832bf870a0252e'
MODERN_COMMIT='56a9a2c018385cd5acef015378cae7f084d1b11c'


class UpstreamBackbone(nn.Module):
    def __init__(self,name,context,horizon,channels,vendor='vendor',**overrides):
        super().__init__(); self.name=name
        root=Path(vendor).resolve()
        src=root/'ModernTCN'/'ModernTCN-Long-term-forecasting' if name=='ModernTCN' else root/'Time-Series-Library'
        if not src.exists(): raise FileNotFoundError('Run python scripts/fetch_backbones.py first')
        # Both upstream projects use top-level models/layers packages.
        for module in list(sys.modules):
            if module in {'models','layers','utils'} or module.startswith(('models.','layers.','utils.')):
                del sys.modules[module]
        sys.path.insert(0,str(src))
        config=dict(task_name='long_term_forecast',seq_len=context,pred_len=horizon,label_len=context//2,
                    enc_in=channels,dec_in=channels,c_out=channels,d_model=32,d_ff=64,n_heads=4,e_layers=2,
                    d_layers=1,dropout=0.,head_dropout=0.,fc_dropout=0.,embed='timeF',freq='h',factor=3,
                    activation='gelu',output_attention=False,patch_len=16,stride=8,moving_avg=25,
                    channel_independence=1,down_sampling_layers=1,down_sampling_window=2,
                    down_sampling_method='avg',decomp_method='moving_avg',top_k=5,use_norm=1,
                    stem_ratio=4,downsample_ratio=2,ffn_ratio=2,num_blocks=[1,1,1,1],large_size=[31,29,27,13],
                    small_size=[5,5,5,5],dims=[32,32,32,32],dw_dims=[32,32,32,32],small_kernel_merged=False,use_multi_scale=False,
                    revin=True,affine=True,subtract_last=False,individual=False,kernel_size=25,
                    patch_size=8,patch_stride=4,decomposition=False)
        config.update(overrides);self.config=config
        self.network=importlib.import_module('models.'+name).Model(SimpleNamespace(**config))
        # Unused heads/layers occur in upstream multitask implementations. Remove
        # only parameters absent from the forecasting graph, retaining the model.
        self.network.zero_grad(set_to_none=True)
        self.forward(torch.randn(2,context,channels)).sum().backward()
        self.inactive_parameters=[]
        for pname,p in self.network.named_parameters():
            if p.grad is None:
                p.requires_grad_(False);self.inactive_parameters.append(pname)
        self.network.zero_grad(set_to_none=True)

    def forward(self,x):
        if self.name=='ModernTCN': return self.network(x)
        return self.network(x,None,None,None)

    def parameter_blocks(self):
        groups={};seen=set()
        for name,module in self.network.named_modules():
            params=[p for p in module.parameters(recurse=False) if p.requires_grad and id(p) not in seen]
            if params:
                groups[name]=params;seen.update(map(id,params))
        return groups


def make_backbone(name,context,horizon,channels,**kwargs):
    return DLinear(context,horizon,channels) if name=='DLinear' else UpstreamBackbone(name,context,horizon,channels,**kwargs)
