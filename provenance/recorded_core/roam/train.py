import copy
import time
import numpy as np
import torch
from .optimizer import ROAMOptimizer
from .controls import Controls
from .data import sample_batch,evaluate
from .models import module_blocks
from .descriptors import gradient_disagreement,trajectory_descriptors


def synchronize(device):
    if str(device).startswith('cuda'):
        torch.cuda.synchronize()


def describe(model,data,seed,batch_size=64,classification=False):
    device=next(model.parameters()).device
    rng=torch.Generator(device=device).manual_seed(seed+50000)
    b1=sample_batch(data['train'],batch_size,rng); b2=sample_batch(data['train'],batch_size,rng)
    gns=gradient_disagreement(model,b1,b2,classification)
    return trajectory_descriptors(data['trajectory'],data['metadata']['horizon'],data['metadata']['context'],gns)


def fit(model_factory,data,seed=0,method='roam',controls=None,lr=1e-3,
        weight_decay=0.,steps=1000,batch_size=64,eval_every=200,
        metric=True,switching='discrete',classification=False,test=False):
    torch.manual_seed(seed)
    device=data['train'][0].device
    model=model_factory().to(device)
    initial=copy.deepcopy(model.state_dict())
    rng=torch.Generator(device=device).manual_seed(seed+10000)
    probe_rng=torch.Generator(device=device).manual_seed(seed+20000)
    if method=='roam':
        opt=ROAMOptimizer(model,controls,lr,weight_decay,metric,switching,classification=classification,seed=seed)
    elif method=='adamw':
        opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=weight_decay)
    else:
        raise ValueError(method)
    best=float('inf'); best_state=None; history=[]; calls=0
    synchronize(device); start=time.perf_counter()
    if device.type=='cuda':
        torch.cuda.reset_peak_memory_stats()
    for step in range(1,steps+1):
        batch=sample_batch(data['train'],batch_size,rng)
        if method=='roam':
            probe=tuple(sample_batch(data['train'],batch_size,probe_rng) for _ in range(2)) if step%10==0 else None
            diagnostic=opt.step(batch,probe)
        else:
            opt.zero_grad(set_to_none=True)
            output=model(batch[0])
            loss=torch.nn.functional.cross_entropy(output,batch[1]) if classification else torch.nn.functional.mse_loss(output,batch[1])
            loss.backward(); opt.step()
            diagnostic={'train_batch_loss':float(loss.detach()),'phase':1}
        if step%eval_every==0 or step==steps:
            val=evaluate(model,data['val'],classification); calls+=1
            synchronize(device)
            history.append({'step':step,'seconds':time.perf_counter()-start,'val':val,**diagnostic})
            if np.isfinite(val['loss']) and val['loss']<best:
                best=val['loss']; best_state=copy.deepcopy(model.state_dict())
    synchronize(device); elapsed=time.perf_counter()-start
    if best_state is None:
        raise RuntimeError('No finite validation checkpoint')
    final_state=copy.deepcopy(model.state_dict())
    final_train=evaluate(model,data['train'],classification)
    model.load_state_dict(best_state)
    selected_train=evaluate(model,data['train'],classification)
    metrics=evaluate(model,data['test'],classification) if test else None
    counts=opt.counts if method=='roam' else {'forward':steps,'backward':steps,'phase2_steps':0,'phase_entries':0}
    result={'seed':seed,'method':method,'lr':lr,'weight_decay':weight_decay,'steps':steps,'batch_size':batch_size,'metric':metric,'switching':switching,'controls':controls.to_dict() if controls else None,'val':best,'test':metrics,'selected_train':selected_train,'final_train':final_train,'seconds':elapsed,'gpu_hours':elapsed/3600 if device.type=='cuda' else 0.,'peak_cuda_bytes':torch.cuda.max_memory_allocated() if device.type=='cuda' else 0,'validation_calls':calls,'counts':dict(counts),'history':history}
    return result,best_state,final_state


def population_fit(model_factory,data,seed,controls,lr=1e-3,steps=1000,
                   batch_size=64,metric=True,switching='discrete',outer=True,
                   classification=False,time_weight=0.,memory_weight=0.,test=True,
                   initial_controls=None,wall_seconds=None,rounds=5):
    """Four serial members; common round boundary and resource objective.

    The evaluation interval is fixed at 200 in the matched-query experiments.
    Each member has an independent control perturbation and identical batches.
    """
    device=data['train'][0].device
    np_rng=np.random.default_rng(seed+30000)
    torch.manual_seed(seed)
    template=model_factory().to(device); initial=copy.deepcopy(template.state_dict())
    members=[]
    for i in range(4):
        model=model_factory().to(device); model.load_state_dict(initial)
        ctl=copy.deepcopy(initial_controls[i]) if initial_controls is not None else (copy.deepcopy(controls) if i==0 else controls.perturb(np_rng))
        members.append({'model':model,'opt':ROAMOptimizer(model,ctl,lr,metric=metric,switching=switching,classification=classification,seed=seed), 'seconds':0.})
    best=float('inf'); best_state=None; history=[]; validation_calls=0
    counts={key:0 for key in members[0]['opt'].counts}
    rng=torch.Generator(device=device).manual_seed(seed+10000)
    probe_rng=torch.Generator(device=device).manual_seed(seed+20000)
    synchronize(device); start=time.perf_counter()
    if device.type=='cuda': torch.cuda.reset_peak_memory_stats()
    completed_rounds=0
    for step in range(1,steps+1):
        batch=sample_batch(data['train'],batch_size,rng)
        needs_check=any((m['opt'].step_count+1)%m['opt'].check_every==0 for m in members)
        probe=tuple(sample_batch(data['train'],batch_size,probe_rng) for _ in range(2)) if needs_check else None
        for member in members:
            synchronize(device); member_start=time.perf_counter()
            before=member['opt'].counts.copy()
            member['last']=member['opt'].step(batch,probe)
            for key in counts: counts[key]+=member['opt'].counts[key]-before[key]
            synchronize(device); member['seconds']+=time.perf_counter()-member_start
        elapsed_now=time.perf_counter()-start
        due=(elapsed_now >= wall_seconds*(completed_rounds+1)/rounds) if wall_seconds is not None else (step%controls.eval_interval==0 or step==steps)
        if due:
            completed_rounds+=1
            scores=[]
            for i,member in enumerate(members):
                val=evaluate(member['model'],data['val'],classification); validation_calls+=1
                # Identical model storage; the common memory charge cancels in ranking.
                state_bytes=sum(v.numel()*v.element_size() for v in member['model'].parameters())
                score=val['loss']+time_weight*member['seconds']/max(step,1)+memory_weight*state_bytes/1e6
                scores.append(score)
                history.append({'step':step,'member':i,'val':val,'utility':score,'controls':member['opt'].controls.to_dict(),**member['last']})
                if np.isfinite(val['loss']) and val['loss']<best:
                    best=val['loss']; best_state=copy.deepcopy(member['model'].state_dict())
            if outer and step<steps and (wall_seconds is None or completed_rounds<rounds):
                elite,bottom=int(np.argmin(scores)),int(np.argmax(scores))
                if elite!=bottom:
                    members[bottom]['model'].load_state_dict(members[elite]['model'].state_dict())
                    replacement=copy.deepcopy(members[elite]['opt'].controls).perturb(np_rng)
                    members[bottom]['opt']=ROAMOptimizer(members[bottom]['model'],replacement,lr,metric=metric,switching=switching,classification=classification,seed=seed+step)
            if wall_seconds is not None and completed_rounds>=rounds:
                break
    synchronize(device); elapsed=time.perf_counter()-start
    if best_state is None: raise RuntimeError('Population has no finite checkpoint')
    template.load_state_dict(best_state)
    result={'seed':seed,'method':'roam_population','population':4,'metric':metric,'switching':switching,'outer':outer,'steps_per_member':step,'wall_seconds_cap':wall_seconds,'lr':lr,'batch_size':batch_size,'val':best,'test':evaluate(template,data['test'],classification) if test else None,'selected_train':evaluate(template,data['train'],classification),'seconds':elapsed,'gpu_hours':elapsed/3600,'peak_cuda_bytes':torch.cuda.max_memory_allocated() if device.type=='cuda' else 0,'validation_calls':validation_calls,'counts':counts,'history':history,'initial_controls':controls.to_dict(),'resource_weights':{'time':time_weight,'memory':memory_weight}}
    return result,best_state
