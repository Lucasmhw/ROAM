"""Equations (1)--(5), (15) on ordinary parameter blocks.

The numerical realization is diagonal Hutchinson GGN, refreshed at a fixed
cadence. Between refreshes the metric is frozen. Curvature memory is reset
at every metric/control refresh. No dense parameter-by-parameter array is built.
"""
from collections import deque
import math
import torch
from torch.nn import functional as F
from .models import module_blocks
from .controls import Controls


class ROAMOptimizer:
    def __init__(self, model, controls=None, lr=1e-3, weight_decay=0., metric=True,
                 switching='discrete', refresh=100, check_every=10, sketch_rank=2,
                 classification=False, seed=0):
        self.model=model; self.blocks=module_blocks(model)
        self.params=[p for ps in self.blocks.values() for p in ps]
        self.slices=[]; start=0
        for ps in self.blocks.values():
            size=sum(p.numel() for p in ps)
            self.slices.append(slice(start,start+size)); start+=size
        self.controls=controls or Controls.default(len(self.blocks))
        if len(self.controls.alpha) != len(self.blocks):
            raise ValueError('Initializer block count does not match backbone')
        self.lr=lr; self.weight_decay=weight_decay; self.metric_enabled=metric
        self.switching=switching; self.refresh=refresh; self.check_every=check_every
        self.sketch_rank=sketch_rank; self.classification=classification
        ref=self.params[0]
        self.G=torch.ones(start,device=ref.device,dtype=ref.dtype)
        self.D=torch.zeros_like(self.G); self.F=torch.zeros_like(self.G)
        self.m=torch.zeros_like(self.G); self.v=torch.zeros(len(self.slices),device=ref.device,dtype=ref.dtype)
        self.memory=deque(maxlen=10); self.step_count=0; self.phase=1
        self.successes=0; self.failures=0; self.last_chi=float('inf'); self.last_rho=0.
        self.rng=torch.Generator(device=ref.device).manual_seed(seed+991)
        self.counts={'forward':0,'backward':0,'curvature_backward':0,'line_search_forward':0,'accepted_pairs':0,'rejected_pairs':0,'phase2_steps':0,'phase_entries':0,'phase_exits':0,'metric_refreshes':0,'line_search_failures':0,'fallback_directions':0}

    def flat(self):
        return torch.cat([p.detach().reshape(-1) for p in self.params])

    @torch.no_grad()
    def assign(self,x):
        offset=0
        for p in self.params:
            p.copy_(x[offset:offset+p.numel()].view_as(p)); offset+=p.numel()

    def loss(self,batch,backward=True):
        pred=self.model(batch[0]); self.counts['forward']+=1
        loss=F.cross_entropy(pred,batch[1]) if self.classification else F.mse_loss(pred,batch[1])
        if self.weight_decay:
            loss=loss+.5*self.weight_decay*sum(p.square().sum() for p in self.params)
        if not backward:
            return loss.detach()
        gradients=torch.autograd.grad(loss,self.params)
        self.counts['backward']+=1
        return loss.detach(),torch.cat([g.detach().flatten() for g in gradients])

    def refresh_metric(self,batch):
        if not self.metric_enabled:
            self.G.fill_(1.); return
        output=self.model(batch[0]); self.counts['forward']+=1
        diagonal=torch.zeros_like(self.G)
        for j in range(self.sketch_rank):
            if self.classification:
                probs=output.detach().softmax(-1)
                labels=torch.multinomial(probs,1,generator=self.rng).squeeze(-1)
                signs=torch.randint(0,2,(len(output),),device=output.device,generator=self.rng).mul(2).sub(1)
                score=-(F.cross_entropy(output,labels,reduction='none')*signs).sum()/math.sqrt(len(output))
            else:
                signs=torch.randint(0,2,output.shape,device=output.device,generator=self.rng).mul(2).sub(1)
                score=(output*signs).sum()*math.sqrt(2/output.numel())
            gradients=torch.autograd.grad(score,self.params,retain_graph=j+1<self.sketch_rank)
            diagonal+=torch.cat([g.detach().flatten() for g in gradients]).square()/self.sketch_rank
            self.counts['backward']+=1; self.counts['curvature_backward']+=1
        self.F.copy_(diagonal)
        for i,sl in enumerate(self.slices):
            q=self.controls.damping[i]+1e-6+self.controls.omega[i]*self.F[sl]+(1-self.controls.omega[i])*self.D[sl]
            self.G[sl]=self.controls.alpha[i]*q
        self.memory.clear()
        self.phase=1
        self.successes=0; self.failures=0; self.last_rho=0.
        self.counts['metric_refreshes']+=1

    def set_controls(self,controls):
        self.controls=controls
        self.memory.clear(); self.phase=1; self.successes=0; self.failures=0
        self.last_rho=0.; self._force_refresh=True

    def dot(self,a,b):
        return torch.dot(a*self.G,b)

    def lbfgs_direction(self,g):
        if not self.memory:
            return -g
        q=g.clone(); alphas=[]
        for s,y,rho in reversed(self.memory):
            a=rho*self.dot(s,q); alphas.append(a); q-=a*y
        s,y,_=self.memory[-1]
        scale=self.dot(s,y)/self.dot(y,y).clamp_min(1e-20)
        r=scale.clamp(1e-8,1e8)*q
        for (s,y,rho),a in zip(self.memory,reversed(alphas)):
            r+=s*(a-rho*self.dot(y,r))
        return -r

    def step(self,batch,independent_batch=None):
        self.step_count+=1; t=self.step_count
        if t==1 or (t-1)%self.refresh==0 or getattr(self,'_force_refresh',False):
            self.refresh_metric(batch); self._force_refresh=False
        loss,h=self.loss(batch); old=self.flat(); g=h/self.G
        self.D.mul_(.999).addcmul_(h,h,value=.001)
        self.m.mul_(.9).add_(g,alpha=.1)
        first=torch.empty_like(g)
        for i,sl in enumerate(self.slices):
            moment=self.dot_block(g,sl)/(sl.stop-sl.start)
            self.v[i]=.999*self.v[i]+.001*moment
            u=(.1*g[sl]+.9*self.m[sl]/(1-.9**t))/(torch.sqrt(self.v[i]/(1-.999**t))+1e-8)
            first[sl]=-self.lr*u
        use_qn=self.switching=='discrete' and self.phase==2 and bool(self.memory)
        blend=self.switching=='blend' and bool(self.memory)
        direction=first
        if use_qn:
            direction=self.lbfgs_direction(g); self.counts['phase2_steps']+=1
        elif blend:
            a=1/(1+self.last_chi/max(self.controls.tau_chi,1e-8))
            a*=max(self.last_rho,0)/(max(self.last_rho,0)+self.controls.tau_rho)
            direction=(1-a)*first+a*self.lbfgs_direction(g)
        if use_qn or blend:
            slope=torch.dot(h,direction)
            if slope>=0 or not torch.isfinite(slope):
                direction=-self.lr*g; slope=torch.dot(h,direction)
                self.counts['fallback_directions']+=1
            accepted=False; step=1.
            for _ in range(10):
                self.assign(old+step*direction)
                with torch.no_grad():
                    trial=self.loss(batch,False)
                self.counts['line_search_forward']+=1
                if torch.isfinite(trial) and trial<=loss+1e-4*step*slope:
                    accepted=True; break
                step*=.5
            if not accepted:
                self.assign(old); self.counts['line_search_failures']+=1
        else:
            self.assign(old+direction)
        if t%self.check_every==0 or use_qn or blend:
            _,hn=self.loss(batch); gn=hn/self.G
            s=self.flat()-old; y=gn-g
            ss=self.dot(s,s); sy=self.dot(s,y)
            valid=bool(ss>0 and sy>=1e-4*ss and torch.isfinite(sy))
            self.last_rho=float(sy/(ss+1e-8)) if valid else 0.
            if valid:
                self.memory.append((s.detach(),y.detach(),1/sy))
                self.counts['accepted_pairs']+=1
            else:
                self.counts['rejected_pairs']+=1
            if t%self.check_every==0 and independent_batch is not None:
                _,h1=self.loss(independent_batch[0]); g1=h1/self.G
                _,h2=self.loss(independent_batch[1]); g2=h2/self.G
                self.last_chi=float(self.dot(g1-g2,g1-g2)/(self.dot((g1+g2)/2,(g1+g2)/2)+1e-8))
                good=valid and self.last_chi<=self.controls.tau_chi and self.last_rho>=self.controls.tau_rho
                self.successes=self.successes+1 if good else 0
                self.failures=0 if good else self.failures+1
                if self.switching=='discrete':
                    if self.phase==1 and self.successes>=3:
                        self.phase=2; self.counts['phase_entries']+=1
                    elif self.phase==2 and self.failures>=3:
                        self.phase=1; self.counts['phase_exits']+=1
        return {'train_batch_loss':float(loss),'phase':self.phase,'chi':self.last_chi,'rho':self.last_rho,'pairs':len(self.memory)}

    def dot_block(self,a,sl):
        return torch.dot(a[sl]*self.G[sl],a[sl])
