from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np


@dataclass
class Controls:
    alpha: list
    damping: list
    omega: list
    tau_chi: float = 2.
    tau_rho: float = 1e-4
    sigma: float = .2
    eval_interval: int = 200

    @classmethod
    def default(cls, blocks):
        return cls([1.]*blocks,[1e-3]*blocks,[.5]*blocks)

    def to_dict(self):
        return asdict(self)

    def latent(self):
        positive = np.r_[self.alpha,self.damping,self.tau_chi,self.tau_rho,self.sigma]
        invsoft = np.log(np.expm1(np.maximum(positive,1e-10)))
        omega = np.clip(self.omega,1e-6,1-1e-6)
        return np.r_[invsoft,np.log(omega/(1-omega)),float(self.eval_interval)]

    @classmethod
    def from_latent(cls, z, blocks):
        z=np.asarray(z)
        pos=np.logaddexp(0,z[:2*blocks+3])
        omega=1/(1+np.exp(-np.clip(z[2*blocks+3:3*blocks+3],-30,30)))
        return cls(np.clip(pos[:blocks],.01,100).tolist(),np.clip(pos[blocks:2*blocks],1e-8,10).tolist(),omega.tolist(),float(np.clip(pos[2*blocks],.05,20)),float(np.clip(pos[2*blocks+1],1e-6,1)),float(np.clip(pos[2*blocks+2],.01,1)),int(np.clip(round(z[-1]),25,1000)))

    def perturb(self, rng, evolve_interval=False):
        def mul(x,lo,hi):
            a=np.asarray(x)
            return np.clip(a*np.exp(rng.normal(0,self.sigma,size=a.shape)),lo,hi)
        omega = np.clip(np.asarray(self.omega)+rng.normal(0,self.sigma*.2,len(self.omega)),.01,.99)
        return Controls(mul(self.alpha,.01,100).tolist(),mul(self.damping,1e-8,10).tolist(),omega.tolist(),float(mul(self.tau_chi,.05,20)),float(mul(self.tau_rho,1e-6,1)),float(mul(self.sigma,.01,1)),int(mul(self.eval_interval,25,1000)) if evolve_interval else self.eval_interval)


class AffineInitializer:
    """Ridge fit to source-task, validation-selected latent controls.

    The original PDF does not identify its W,b. This is the explicit fitting
    protocol for the experiments in this repository; it does not recover them.
    """
    def __init__(self, mean, scale, W, bias, blocks, provenance=None):
        self.mean=np.asarray(mean); self.scale=np.asarray(scale)
        self.W=np.asarray(W); self.bias=np.asarray(bias)
        self.blocks=blocks; self.provenance=provenance or {}

    @classmethod
    def fit(cls, descriptors, controls, ridge=1., provenance=None):
        c=np.asarray(descriptors); z=np.asarray([v.latent() for v in controls])
        mean,scale=c.mean(0),c.std(0)
        scale[scale < 1e-8]=1.
        x=(c-mean)/scale
        bias=z.mean(0)
        W=np.linalg.solve(x.T@x+ridge*np.eye(x.shape[1]),x.T@(z-bias)).T
        return cls(mean,scale,W,bias,len(controls[0].alpha),provenance)

    def __call__(self, descriptor):
        return Controls.from_latent(self.W@((descriptor-self.mean)/self.scale)+self.bias,self.blocks)

    def save(self,path):
        Path(path).write_text(json.dumps({k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in vars(self).items()},indent=2))

    @classmethod
    def load(cls,path):
        return cls(**json.loads(Path(path).read_text()))
