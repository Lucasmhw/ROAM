import numpy as np
from scipy.ndimage import uniform_filter1d
import torch


def trajectory_descriptors(trajectory, horizon, context, gns, seasonal_bins=3):
    """Training descriptors: DC excluded; top 3 non-DC seasonal bins.

    The moving average uses width 25 and nearest-endpoint extension.
    For classification, horizon=0 is an extension convention, not a forecast.
    """
    x = np.asarray(trajectory,dtype=np.float64)
    if x.ndim != 2:
        raise ValueError('Expected [time, channels]')
    residual = x-uniform_filter1d(x,25,axis=0,mode='nearest')
    snr = np.mean(np.var(x,axis=0)/(np.var(residual,axis=0)+1e-8))
    power = np.abs(np.fft.rfft(x-x.mean(0),axis=0)[1:])**2
    prob = power/(power.sum(0,keepdims=True)+1e-8)
    entropy = -(prob*np.log(prob+1e-8)).sum(0).mean()/np.log(max(len(prob),2))
    seasonality = np.sort(prob,axis=0)[-seasonal_bins:].sum(0).mean()
    if x.shape[1] > 1:
        corr = np.nan_to_num(np.corrcoef(x,rowvar=False))
        density = np.mean(np.abs(corr[np.triu_indices(x.shape[1],1)]) > .5)
    else:
        density = 0.
    return np.array([snr,entropy,seasonality,horizon/context,density,gns],dtype=np.float64)


def flat_grad(model, batch, classification=False):
    output = model(batch[0])
    loss = torch.nn.functional.cross_entropy(output,batch[1]) if classification else torch.nn.functional.mse_loss(output,batch[1])
    grads = torch.autograd.grad(loss,tuple(model.parameters()))
    return torch.cat([g.detach().flatten() for g in grads])


def gradient_disagreement(model, batch1, batch2, classification=False):
    h1,h2 = flat_grad(model,batch1,classification),flat_grad(model,batch2,classification)
    return ((h1-h2).square().sum()/(((h1+h2)/2).square().sum()+1e-8)).item()
