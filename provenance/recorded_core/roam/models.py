"""Backbones. DLinear uses fixed endpoint-padded moving-average decomposition."""
import torch
from torch import nn
from torch.nn import functional as F


def decompose(x, kernel=25):
    trend = F.avg_pool1d(F.pad(x.transpose(1, 2), (kernel//2, kernel//2), mode='replicate'), kernel, stride=1).transpose(1, 2)
    return x - trend, trend


class DLinear(nn.Module):
    def __init__(self, context=96, horizon=96, channels=7):
        super().__init__()
        self.context, self.horizon = context, horizon
        self.seasonal = nn.Linear(context, horizon)
        self.trend = nn.Linear(context, horizon)

    def forward(self, x):
        seasonal, trend = decompose(x)
        return (self.seasonal(seasonal.transpose(1, 2)) + self.trend(trend.transpose(1, 2))).transpose(1, 2)

    def parameter_blocks(self):
        return {'seasonal': list(self.seasonal.parameters()), 'trend': list(self.trend.parameters())}


class TemporalClassifier(nn.Module):
    def __init__(self, channels, classes):
        super().__init__()
        self.encoder = nn.Sequential(nn.Conv1d(channels, 32, 7, padding=3), nn.GELU(), nn.Conv1d(32, 32, 5, padding=2), nn.GELU())
        self.head = nn.Linear(32, classes)

    def forward(self, x):
        return self.head(self.encoder(x.transpose(1, 2)).mean(-1))

    def parameter_blocks(self):
        return {'conv1': list(self.encoder[0].parameters()), 'conv2': list(self.encoder[2].parameters()), 'head': list(self.head.parameters())}


def module_blocks(model):
    """Each parameter belongs to its direct parent module exactly once."""
    if hasattr(model, 'parameter_blocks'):
        return model.parameter_blocks()
    blocks, seen = {}, set()
    for name, module in model.named_modules():
        params = [p for p in module.parameters(recurse=False) if p.requires_grad and id(p) not in seen]
        if params:
            blocks[name or 'root'] = params
            seen.update(map(id, params))
    return blocks
