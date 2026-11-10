"""Recompute manuscript arithmetic from reported aggregate values.

The revised reporting data provide the transfer, descriptor, and factorial
inputs. This script checks aggregation and arithmetic, without rerunning training.
"""
from pathlib import Path
import json
import statistics

root=Path(__file__).resolve().parents[1]
reporting=json.loads((root/'reporting/figures/figure_data.json').read_text(encoding='utf-8'))

data={
'iTransformer':([.454,.384,.408,.292,.261,.176,.364],[.419,.362,.379,.272,.245,.167,.349]),
'PatchTST':([.416,.331,.352,.257,.228,.163,.386],[.389,.315,.330,.244,.219,.156,.378]),
'TimeMixer':([.441,.392,.388,.278,.245,.182,.397],[.413,.369,.362,.262,.232,.174,.382]),
'ModernTCN':([.428,.365,.366,.266,.236,.170,.372],[.401,.348,.347,.251,.225,.163,.358]),
'DLinear':([.433,.469,.359,.283,.247,.167,.381],[.403,.421,.341,.258,.233,.160,.352]),
}
audit={'scope':'arithmetic of rounded manuscript entries only','macro':{}}
for name,(base,roam) in data.items():
    audit['macro'][name]={'baseline_mean':statistics.mean(base),'roam_mean':statistics.mean(roam),'relative_gain_percent':100*(1-sum(roam)/sum(base)),'all_seven_cells_lower':all(r<b for b,r in zip(base,roam))}
f={tuple(row[:3]):row[3] for row in reporting['factorial']['rows']}
audit['factorial']={name:sum(v-f[tuple(1 if j==i else c for j,c in enumerate(key))] for key,v in f.items() if key[i]==0)/4 for i,name in enumerate(['metric','switching','outer'])}
transfer=reporting['transfer']
audit['transfer']=[{'source':src,'target':dst,'baseline_mse':base,'roam_mse':roam,'relative_gain_percent':100*(1-roam/base)} for src,dst,base,roam in zip(transfer['sources'],transfer['targets'],transfer['baseline'],transfer['roam'])]
assert [round(row['relative_gain_percent'],2) for row in audit['transfer']]==[6.89,5.24,5.97,5.41]
descriptor=reporting['descriptor']
audit['descriptor_relative_increase_percent']={name:100*(value/descriptor['reference']-1) for name,value in zip(descriptor['labels'],descriptor['mse'])}
audit['factorial_settings']={key:reporting['setting_metadata'][key] for key in ['factorial_A','factorial_B','factorial_C']}
audit['convex_four_horizon_means']={key:statistics.mean(reporting['convex'][key]) for key in ['adamw2k_test','adamw10k_test','roam2k_test']}
audit['aggregation_notes']={
    'transfer':'Four individually reported pairs; other matrix cells are NR. The 12-transfer aggregate is separate.',
    'weather':'The horizon-specific tournament and four-horizon backbone average have distinct scopes even when both round to .232.',
    'first_task':'The calibration-inclusive comparison uses three matched seeds; target-adaptation comparisons use ten seeds.',
    'figures':'Final figure numbers and page locations are in reporting/05_Figure_Captions_and_Placement.md.',
}
out=root/'results/manuscript_arithmetic_audit.json';out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8');print(json.dumps(audit,indent=2))
