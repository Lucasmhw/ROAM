"""Re-evaluate released checkpoints and compare against their run records."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import torch
from roam.models import DLinear,TemporalClassifier
from roam.data import forecast_data,evaluate
from roam.classification import load_har


def main(a):
    torch.set_num_threads(4);root=Path(a.root);checks=[]
    for name in ['ETTh2','ETTm2']:
        data=forecast_data(name,96,96,root=a.data,device=a.device)
        paths=list((root/'suite').glob(f'target_{name}_96_*.json'))+list((root/'coldstart').glob(f'{name}_seed*.json'))
        assert len(paths)==63
        for path in paths:
            record=json.loads(path.read_text());model=DLinear(96,96,7).to(a.device)
            model.load_state_dict(torch.load(path.parent/'checkpoints'/path.with_suffix('.pt').name,map_location=a.device,weights_only=True))
            measured=evaluate(model,data['test']);difference=abs(measured['mse']-record['test']['mse'])
            assert difference<1e-6,(path,difference)
            checks.append({'record':path.relative_to(root).as_posix(),'metric':'test_mse','absolute_difference':difference})
            for split,expected in [('val',record['val']),('train',record['selected_train']['loss'])]:
                difference=abs(evaluate(model,data[split])['loss']-expected)
                assert difference<1e-6,(path,split,difference)
                checks.append({'record':path.relative_to(root).as_posix(),'metric':split+'_loss','absolute_difference':difference})
    data=load_har(a.data,a.device);paths=list((root/'classification').glob('target_*.json'));assert len(paths)==50
    for path in paths:
        record=json.loads(path.read_text());model=TemporalClassifier(9,6).to(a.device)
        model.load_state_dict(torch.load(path.parent/'checkpoints'/path.with_suffix('.pt').name,map_location=a.device,weights_only=True))
        measured=evaluate(model,data['test'],True)
        for key in ['accuracy','loss']:
            difference=abs(measured[key]-record['test'][key]);assert difference<1e-6,(path,key,difference)
            checks.append({'record':path.relative_to(root).as_posix(),'metric':key,'absolute_difference':difference})
        for split,expected in [('val',record['val']),('train',record['selected_train']['loss'])]:
            difference=abs(evaluate(model,data[split],True)['loss']-expected)
            assert difference<1e-6,(path,split,difference)
            checks.append({'record':path.relative_to(root).as_posix(),'metric':split+'_loss','absolute_difference':difference})
    report={'forecast_checkpoints':126,'classification_checkpoints':50,'checks':checks,'maximum_absolute_difference':max(c['absolute_difference'] for c in checks),'tolerance':1e-6}
    (root/'checkpoint_verification.json').write_text(json.dumps(report,indent=2));print('Verified 176 checkpoints;',report['maximum_absolute_difference'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='results');p.add_argument('--data',default='data');p.add_argument('--device',default='cuda');main(p.parse_args())
