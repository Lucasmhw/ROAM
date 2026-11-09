"""Generate all supplementary tables from complete, per-seed JSON records."""
import argparse
import csv
import json
import math
import statistics as stats
from pathlib import Path


def read(p):return json.loads(Path(p).read_text())
def describe(values):
    return {'n':len(values),'mean':stats.mean(values),'sd':stats.stdev(values) if len(values)>1 else 0.,'min':min(values),'max':max(values)}
def pretty(summary,digits=4):return f"{summary['mean']:.{digits}f} ± {summary['sd']:.{digits}f}"
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def collect(folder,pattern,n,strict):
    paths=sorted(folder.glob(pattern));records=[read(p) for p in paths]
    if strict:assert len(records)==n,(pattern,len(records),n)
    seeds=[r['seed'] for r in records]
    assert len(seeds)==len(set(seeds)),pattern
    return records
def summarize(records,classification=False):
    fields={'test_mse':lambda r:r['test']['mse'],'test_mae':lambda r:r['test']['mae']} if not classification else {'test_accuracy':lambda r:100*r['test']['accuracy'],'test_ce':lambda r:r['test']['loss']}
    fields.update({'seconds':lambda r:r['seconds'],'peak_mib':lambda r:r['peak_cuda_bytes']/2**20,'forward':lambda r:r['counts']['forward'],'backward':lambda r:r['counts']['backward'],'validation_calls':lambda r:r['validation_calls'],'selected_train_loss':lambda r:r['selected_train']['loss']})
    if records and 'final_train' in records[0]:fields['final_train_loss']=lambda r:r['final_train']['loss']
    if records and 'steps_per_member' in records[0]:
        fields['member_updates']=lambda r:r['population']*r['steps_per_member']
        fields['member_updates_per_second']=lambda r:r['population']*r['steps_per_member']/r['seconds']
    if records and 'line_search_forward' in records[0]['counts']:
        fields.update({'line_search_forward':lambda r:r['counts']['line_search_forward'],'phase_entries':lambda r:r['counts']['phase_entries'],'phase2_steps':lambda r:r['counts']['phase2_steps'],'line_search_failures':lambda r:r['counts']['line_search_failures']})
    return {name:describe([fn(r) for r in records]) for name,fn in fields.items()} if records else {}
def paired(a,b,key='mse'):
    aa={r['seed']:r['test'][key] for r in a};bb={r['seed']:r['test'][key] for r in b}
    seeds=sorted(set(aa)&set(bb));delta=[bb[s]-aa[s] for s in seeds]
    if not delta:return {}
    result=describe(delta);result['direction']='comparator minus conditioned; positive favors conditioned for MSE'
    if len(delta)>1:
        from scipy.stats import t
        radius=float(t.ppf(.975,len(delta)-1))*result['sd']/math.sqrt(len(delta))
        result['exploratory_unadjusted_95ci']=[result['mean']-radius,result['mean']+radius]
    return result


def main(a):
    root=Path(a.root);suite=root/'suite';output=root/'summary';output.mkdir(exist_ok=True)
    result={'forecasting':{},'convex':{},'classification':{},'coldstart':{},'calibration':read(suite/'calibration_summary.json'),'notes':['All table selections use validation; test metrics are reporting only.','Standard deviations use ddof=1.','Paired confidence intervals are exploratory and unadjusted for multiple comparisons.','Timing covers the recorded training/validation phase, excluding data loading, descriptor construction, and final evaluations.']}
    target_records={};rows=[];cost_rows=[];switch_rows=[]
    arms=['conditioned','source_mean','direct_search','continuous_blend','phase_i_only','identity']
    labels={'conditioned':'Conditioned','source_mean':'Source mean','direct_search':'Direct search','continuous_blend':'Continuous blend','phase_i_only':'Phase I only','identity':'Identity metric'}
    for name in ['ETTh2','ETTm2']:
        result['forecasting'][name]={};target_records[name]={}
        for arm in arms:
            records=collect(suite,f'target_{name}_96_{arm}_seed*.json',10,a.strict)
            target_records[name][arm]=records;s=summarize(records)
            if not s:continue
            result['forecasting'][name][arm]=s
            if arm in arms[:3]:rows.append([name,labels[arm],pretty(s['test_mse']),pretty(s['test_mae'])])
            if arm in ['conditioned','identity','phase_i_only']:
                cost_rows.append([name,labels[arm],f"{s['seconds']['mean']:.2f}",f"{s['peak_mib']['mean']:.1f}",f"{s['member_updates_per_second']['mean']:.0f}",f"{s['forward']['mean']:.0f}",f"{s['backward']['mean']:.0f}"])
            if arm in ['conditioned','continuous_blend','phase_i_only']:
                switch_rows.append([name,labels[arm],pretty(s['test_mse']),f"{s['member_updates_per_second']['mean']:.0f}",f"{s['line_search_forward']['mean']:.0f}",f"{s['seconds']['mean']:.2f}"])
        result['forecasting'][name]['paired']={arm:paired(target_records[name]['conditioned'],target_records[name][arm]) for arm in arms[1:]}
    tables={'initializer':table(['Target','Initialization','Test MSE','Test MAE'],rows),'metric_cost':table(['Target','Arm','Seconds','Peak MiB','Updates/s','Forward','Backward'],cost_rows),'switch':table(['Target','Policy','Test MSE','Updates/s','Line-search forwards','Seconds'],switch_rows)}
    convex_rows=[];convex_full=[]
    for name,h in [('ETTh2',96),('ETTh2',192),('ETTh2',336),('ETTh2',720),('ETTm2',96)]:
        exact_path=root/'exact'/f'{name}_{h}.json'
        if not exact_path.exists():
            if a.strict:raise FileNotFoundError(exact_path)
            continue
        exact=read(exact_path);entry={'exact':exact,'arms':{}}
        selected=[]
        for arm in ['adamw_zero','adamw_zero_extended','roam_zero_tuned','roam_single','adamw_tuned','adamw_extended']:
            if arm.startswith('adamw_zero') or arm=='roam_zero_tuned':folder=root/'convex_zero';pattern=f'{name}_{h}_{arm}_seed*.json'
            else:folder=suite;pattern=f'convex_{name}_{h}_{arm}_seed*.json'
            records=collect(folder,pattern,10,a.strict);s=summarize(records)
            if not s:continue
            entry['arms'][arm]=s
            convex_full.append([name,str(h),arm,pretty(s['final_train_loss']),pretty(s['selected_train_loss']),pretty(s['test_mse']),pretty(s['test_mae']),pretty(s['seconds'],2)])
            if arm in ['adamw_zero','adamw_zero_extended','roam_zero_tuned']:selected.append(pretty(s['test_mse']))
        result['convex'][f'{name}_{h}']=entry
        if len(selected)==3:convex_rows.append([f'{name}/{h}',*selected,f"{exact['test']['mse']:.4f}"])
        convex_full.append([name,str(h),'Exact unregularized',f"{exact['train']['mse']:.6f}",f"{exact['train']['mse']:.6f}",f"{exact['test']['mse']:.6f}",f"{exact['test']['mae']:.6f}",f"{exact['seconds']:.2f} CPU"])
    tables['convex']=table(['Task/horizon','AdamW 2k, WD=0','AdamW 10k, WD=0','ROAM 2k','Exact LS'],convex_rows)
    tables['convex_full']=table(['Dataset','H','Method','Final train MSE','Selected train MSE','Test MSE','Test MAE','Seconds'],convex_full)
    class_rows=[]
    for arm in ['conditioned','source_mean','direct_search','continuous_blend','adamw']:
        records=collect(root/'classification',f'target_{arm}_seed*.json',10,a.strict);s=summarize(records,True)
        if not s:continue
        result['classification'][arm]=s
        class_rows.append([labels.get(arm,'AdamW, 1500 updates'),pretty(s['test_accuracy'],2),pretty(s['test_ce']),pretty(s['seconds'],2)])
    tables['classification']=table(['Method','Test accuracy (%)','Test CE','Seconds'],class_rows)
    class_initializer=root/'classification/initializer.json'
    if class_initializer.exists():
        result['classification_calibration']=read(class_initializer)['provenance']
        result['classification_calibration']['validation_calls']=sum(run['validation_calls'] for path in (root/'classification').glob('source_*.json') for run in read(path)['runs'])
    cold_rows=[]
    for name in ['ETTh2','ETTm2']:
        records=collect(root/'coldstart',f'{name}_seed*.json',3,a.strict)
        if not records:continue
        s=summarize(records);s['target_search_seconds']=describe([r['target_search_seconds'] for r in records]);s['target_search_validation_calls']=describe([r['target_search_validation_calls'] for r in records]);s['total_seconds']=describe([r['total_measured_training_seconds'] for r in records]);result['coldstart'][name]=s
        matched=[r for r in target_records[name]['conditioned'] if r['seed']<3]
        q=summarize(matched)
        result['coldstart'][name]['conditioned_matched_seeds']=q
        cold_rows.append([name,pretty(q['test_mse']),pretty(s['test_mse']),f"{result['calibration']['total_source_seconds']+q['seconds']['mean']:.2f}",f"{s['total_seconds']['mean']:.2f}",f"{s['target_search_validation_calls']['mean']:.0f}+20"])
    tables['coldstart']=table(['Target','Conditioned MSE','Direct search MSE','Conditioned seconds','Direct seconds','Direct validation calls'],cold_rows)
    geometry_rows=[];result['curvature']={}
    for name in ['ETTh2','ETTm2']:
        records=collect(root/'curvature',f'{name}_seed*.json',10,a.strict)
        if not records:continue
        result['curvature'][name]={}
        row=[name]
        for arm in ['identity','default','source_mean','conditioned']:
            s=describe([r['arms'][arm]['positive_spectrum_condition'] for r in records]);result['curvature'][name][arm]=s;row.append(pretty(s,1))
        geometry_rows.append(row)
    tables['curvature']=table(['Target','Identity','Default metric','Source mean','Conditioned'],geometry_rows)
    result['tables']=tables
    (output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    report=['# Supplementary experiment tables','Means ± sample SD. See `docs/IMPLEMENTATION.md` for protocols and `summary.json` for full statistics.']
    for key,value in tables.items():
        (output/f'{key}.md').write_text(value+'\n',encoding='utf-8');report.extend(['## '+key.replace('_',' '),value])
    (output/'RESULTS.md').write_text('\n\n'.join(report)+'\n',encoding='utf-8')
    print('Generated',output/'summary.json')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='results');p.add_argument('--strict',action='store_true');main(p.parse_args())
