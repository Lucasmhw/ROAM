"""UCI HAR: official subject-disjoint test, additional subject-disjoint validation."""
from pathlib import Path
import io
import zipfile
import hashlib
import urllib.request
import numpy as np
import torch
from sklearn.model_selection import GroupShuffleSplit
from .data import sample_batch
from .descriptors import trajectory_descriptors,gradient_disagreement

URL='https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip'
SIGNALS=[f'{prefix}_{axis}' for prefix in ['body_acc','body_gyro','total_acc'] for axis in ['x','y','z']]


def load_har(root='data',device='cpu'):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    path=root/'har.zip'
    if not path.exists(): urllib.request.urlretrieve(URL,path)
    archive=zipfile.ZipFile(path)
    inner=[n for n in archive.namelist() if n.endswith('UCI HAR Dataset.zip')]
    if inner: archive=zipfile.ZipFile(io.BytesIO(archive.read(inner[0])))
    def read(suffix,dtype=float):
        matches=[n for n in archive.namelist() if n.endswith(suffix) and not n.startswith('__MACOSX')]
        if len(matches)!=1: raise ValueError((suffix,matches))
        return np.loadtxt(io.BytesIO(archive.read(matches[0])),dtype=dtype)
    xtrain=np.stack([read(f'train/Inertial Signals/{s}_train.txt') for s in SIGNALS],axis=-1)
    xtest=np.stack([read(f'test/Inertial Signals/{s}_test.txt') for s in SIGNALS],axis=-1)
    ytrain=read('train/y_train.txt',int)-1;ytest=read('test/y_test.txt',int)-1
    subjects=read('train/subject_train.txt',int)
    train_idx,val_idx=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=2026).split(xtrain,ytrain,subjects))
    mean=xtrain[train_idx].mean((0,1));std=xtrain[train_idx].std((0,1));std[std<1e-8]=1
    def pair(x,y):
        return torch.tensor((x-mean)/std,dtype=torch.float32,device=device),torch.tensor(y,dtype=torch.long,device=device)
    return {'train':pair(xtrain[train_idx],ytrain[train_idx]),'val':pair(xtrain[val_idx],ytrain[val_idx]),'test':pair(xtest,ytest),
            'train_subjects':subjects[train_idx],
            'metadata':{'dataset':'UCI-HAR','horizon':0,'context':128,'channels':9,'classes':6,'train_subjects':np.unique(subjects[train_idx]).tolist(),'validation_subjects':np.unique(subjects[val_idx]).tolist(),'sizes':[len(train_idx),len(val_idx),len(ytest)],'normalization_mean':mean.tolist(),'normalization_std':std.tolist(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'url':URL}}


def describe_classification(model,data,seed):
    device=next(model.parameters()).device
    rng=torch.Generator(device=device).manual_seed(seed+50000)
    gns=gradient_disagreement(model,sample_batch(data['train'],64,rng),sample_batch(data['train'],64,rng),True)
    # Average independent-window descriptors; do not concatenate window boundaries.
    indices=np.linspace(0,len(data['train'][0])-1,min(256,len(data['train'][0])),dtype=int)
    windows=data['train'][0][indices].cpu().numpy()
    c=np.mean([trajectory_descriptors(w,0,128,0.) for w in windows],axis=0)
    c[-1]=gns
    return c
