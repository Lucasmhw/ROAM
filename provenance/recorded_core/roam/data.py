from pathlib import Path
import hashlib
import json
import urllib.request
import numpy as np
import pandas as pd
import torch


ETT_BASE = 'https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/'


def fetch_ett(name, root='data'):
    if name not in {'ETTh1','ETTh2','ETTm1','ETTm2'}:
        raise ValueError('Automatic download supports the four official ETT datasets.')
    path = Path(root) / (name + '.csv')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(ETT_BASE + path.name, path)
    return path


def forecast_data(name, context=96, horizon=96, root='data', device='cpu'):
    path = fetch_ett(name, root) if name.startswith('ETT') else Path(root) / (name + '.csv')
    frame = pd.read_csv(path)
    values = frame.drop(columns=['date'], errors='ignore').to_numpy(dtype=np.float64)
    if name.startswith('ETT'):
        rate = 4 if name.startswith('ETTm') else 1
        borders = [12*30*24*rate, 16*30*24*rate, 20*30*24*rate]
    else:
        borders = [int(len(values)*.7), int(len(values)*.8), len(values)]
    assert borders[-1] <= len(values)
    mean, std = values[:borders[0]].mean(0), values[:borders[0]].std(0)
    std[std < 1e-8] = 1
    scaled = (values - mean)/std
    tensor = torch.tensor(scaled, dtype=torch.float32, device=device)
    result = {}
    starts = [0, borders[0]-context, borders[1]-context]
    for split, start, end in zip(['train','val','test'], starts, borders):
        windows = tensor[start:end].unfold(0, context+horizon, 1).permute(0,2,1)
        result[split] = (windows[:,:context].contiguous(), windows[:,context:].contiguous())
    result['trajectory'] = scaled[:borders[0]]
    result['metadata'] = {'dataset': name, 'context':context, 'horizon':horizon, 'channels':values.shape[1], 'borders':borders, 'mean':mean.tolist(), 'std':std.tolist(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return result


def sample_batch(pair, batch_size, generator):
    x,y = pair
    idx = torch.randint(len(x),(batch_size,),generator=generator, device=x.device)
    return x[idx],y[idx]


@torch.no_grad()
def evaluate(model, pair, classification=False, batch_size=512):
    was_training = model.training
    model.eval()
    x,y = pair
    error, absolute, correct, count = 0.,0.,0,0
    for i in range(0,len(x),batch_size):
        prediction = model(x[i:i+batch_size])
        target = y[i:i+batch_size]
        if classification:
            error += torch.nn.functional.cross_entropy(prediction,target,reduction='sum').item()
            correct += (prediction.argmax(-1)==target).sum().item()
            count += len(target)
        else:
            diff = prediction-target
            error += diff.square().sum().item()
            absolute += diff.abs().sum().item()
            count += diff.numel()
    model.train(was_training)
    if classification:
        return {'loss':error/count,'accuracy':correct/count}
    return {'loss':error/count,'mse':error/count,'mae':absolute/count}
