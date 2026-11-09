"""Arithmetic audit of values transcribed from the supplied manuscript.

This checks arithmetic, not the underlying experiments. It deliberately does
not fabricate per-horizon or per-seed observations from aggregate tables.
"""
from pathlib import Path
import json
import statistics

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
f={(0,0,0):.333,(1,0,0):.323,(0,1,0):.329,(0,0,1):.327,(1,1,0):.318,(1,0,1):.319,(0,1,1):.324,(1,1,1):.312}
audit['factorial']={name:sum(v-f[tuple(1 if j==i else c for j,c in enumerate(key))] for key,v in f.items() if key[i]==0)/4 for i,name in enumerate(['metric','switching','outer'])}
audit['transfer_conflicts']=[{'pair':'ETTm1 -> Weather','figure6_percent':0.,'table20_percent':5.2},{'pair':'Weather -> ECL','figure6_percent':0.,'table20_percent':6.0},{'pair':'ECL -> Exchange','figure6_percent':0.,'table20_percent':5.4}]
audit['unresolved']=['Original per-run logs and initializer coefficients are not available.','No original backbone is identified for each Table 13 setting.','The repeated rounded Weather value does not establish either a contradiction or correct provenance.','Figure 6 and Table 20 cannot both specify the same cell-level gains as labeled; averaging does not resolve these entries.']
out=Path('results/manuscript_arithmetic_audit.json');out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
