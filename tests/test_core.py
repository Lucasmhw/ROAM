import numpy as np
import torch
from roam.models import DLinear
from roam.optimizer import ROAMOptimizer
from roam.controls import Controls,AffineInitializer


def test_dlinear_is_affine_and_has_no_optimizer_constraints():
    torch.manual_seed(4)
    model=DLinear(12,4,2).double()
    x=torch.randn(7,12,2,dtype=torch.float64)
    params=[p.detach().clone() for p in model.parameters()]
    delta=[torch.randn_like(p) for p in model.parameters()]
    y0=model(x).detach()
    with torch.no_grad():
        for p,d in zip(model.parameters(),delta): p.add_(d)
    y1=model(x).detach()
    with torch.no_grad():
        for p,p0,d in zip(model.parameters(),params,delta): p.copy_(p0+.37*d)
    assert torch.allclose(model(x),y0+.37*(y1-y0),atol=1e-10)


def test_metric_spd_and_duality_and_curvature_reset():
    torch.manual_seed(2)
    model=DLinear(12,4,2).double()
    opt=ROAMOptimizer(model,refresh=3,check_every=1)
    batch=(torch.randn(8,12,2,dtype=torch.float64),torch.randn(8,4,2,dtype=torch.float64))
    opt.refresh_metric(batch)
    assert (opt.G>0).all()
    _,h=opt.loss(batch)
    v=torch.randn_like(h)
    assert torch.allclose(opt.dot(h/opt.G,v),torch.dot(h,v),atol=1e-12)
    opt.memory.append((v,v,1/opt.dot(v,v)))
    opt.refresh_metric(batch)
    assert not opt.memory


def test_bfgs_direction_is_descent_in_current_metric():
    model=DLinear(12,4,2).double()
    opt=ROAMOptimizer(model)
    opt.G=torch.rand_like(opt.G)+.1
    for _ in range(5):
        s=torch.randn_like(opt.G); y=s*(torch.rand_like(s)+.1)
        opt.memory.append((s,y,1/opt.dot(s,y)))
    g=torch.randn_like(opt.G)
    assert opt.dot(g,opt.lbfgs_direction(g)) < 0


def test_hutchinson_matches_tiny_exact_ggn_in_expectation():
    torch.manual_seed(2)
    model=torch.nn.Linear(3,2,bias=False).double()
    batch=(torch.randn(9,3,dtype=torch.float64),torch.zeros(9,2,dtype=torch.float64))
    opt=ROAMOptimizer(model,sketch_rank=2000)
    opt.refresh_metric(batch)
    exact=batch[0].square().mean(0).repeat(2)
    assert torch.allclose(opt.F,exact,rtol=.12,atol=.03)


def test_softmax_sketch_matches_exact_fisher_diagonal():
    torch.manual_seed(23)
    model=torch.nn.Linear(3,2,bias=False).double()
    inputs=torch.randn(11,3,dtype=torch.float64)
    batch=(inputs,torch.zeros(11,dtype=torch.long))
    probabilities=model(inputs).detach().softmax(-1)
    # Analytic cross-entropy curvature for a linear softmax model, averaged
    # over examples. This reference uses neither sampled labels nor VJPs.
    exact=((probabilities*(1-probabilities))[:,:,None]*inputs[:,None,:].square()).mean(0).flatten()
    opt=ROAMOptimizer(model,classification=True,sketch_rank=3000,seed=23)
    opt.refresh_metric(batch)
    assert torch.allclose(opt.F,exact,rtol=.10,atol=.01)


def test_affine_fit_and_roundtrip(tmp_path):
    rng=np.random.default_rng(7); descriptors=rng.normal(size=(12,6))
    controls=[Controls.default(2) for _ in range(12)]
    affine=AffineInitializer.fit(descriptors,controls)
    path=tmp_path/'initializer.json'; affine.save(path)
    loaded=AffineInitializer.load(path)
    assert np.allclose(loaded(descriptors[0]).alpha,[1,1])
    assert np.allclose(loaded(descriptors[0]).damping,[1e-3,1e-3])


def test_disagreement_uses_two_fresh_destination_batches():
    model=torch.nn.Linear(1,1,bias=False).double()
    with torch.no_grad():model.weight.fill_(.5)
    opt=ROAMOptimizer(model,metric=False,check_every=1,switching='none')
    def batch(x,y):return torch.tensor([[x]],dtype=torch.float64),torch.tensor([[y]],dtype=torch.float64)
    opt.step(batch(1.,0.),(batch(2.,1.),batch(3.,-1.)))
    w=model.weight.item()
    h1=2*(2*w-1)*2;h2=2*(3*w+1)*3
    expected=(h1-h2)**2/(((h1+h2)/2)**2+1e-8)
    assert abs(opt.last_chi-expected)<1e-10


def test_switching_requires_three_successes_and_three_failures():
    model=torch.nn.Linear(1,1,bias=False).double()
    with torch.no_grad():model.weight.fill_(.5)
    opt=ROAMOptimizer(model,metric=False,check_every=1)
    train=(torch.ones(4,1,dtype=torch.float64),torch.zeros(4,1,dtype=torch.float64))
    for _ in range(2):
        opt.step(train,(train,train));assert opt.phase==1
    opt.step(train,(train,train));assert opt.phase==2
    bad1=(train[0],torch.ones_like(train[1]));bad2=(train[0],-torch.ones_like(train[1]))
    for _ in range(2):
        opt.step(train,(bad1,bad2));assert opt.phase==2
    opt.step(train,(bad1,bad2));assert opt.phase==1
    assert opt.counts['phase_entries']==1 and opt.counts['phase_exits']==1


def test_forecasting_normalization_and_target_boundaries(tmp_path):
    import pandas as pd
    from roam.data import forecast_data
    values=np.arange(100,dtype=float);values[70:]+=10000
    pd.DataFrame({'date':np.arange(100),'value':values}).to_csv(tmp_path/'Tiny.csv',index=False)
    data=forecast_data('Tiny',4,2,tmp_path)
    assert abs(data['metadata']['mean'][0]-34.5)<1e-12
    assert abs(data['trajectory'].mean())<1e-12
    def unscale(t):return t.double().numpy()*data['metadata']['std'][0]+data['metadata']['mean'][0]
    assert np.allclose(unscale(data['train'][1][-1,:,0]),values[68:70],atol=1e-4)
    assert np.allclose(unscale(data['val'][1][0,:,0]),values[70:72],atol=1e-3)
    assert np.allclose(unscale(data['val'][1][-1,:,0]),values[78:80],atol=1e-3)
    assert np.allclose(unscale(data['test'][1][0,:,0]),values[80:82],atol=1e-3)
