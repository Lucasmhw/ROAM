"""Check selection provenance, budgets, initial populations, and subject splits.

This inspects completed records without fitting models or selecting by test loss.
Checkpoint re-evaluation is performed separately by verify_checkpoints.py.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from roam.controls import Controls, AffineInitializer


def read(path):
    return json.loads(path.read_text())


def check_selection(record, test_expected):
    assert (record['test'] is not None) == test_expected
    losses = [item['val']['loss'] for item in record['history']]
    assert losses and np.isfinite(losses).all()
    assert abs(min(losses) - record['val']) < 1e-12
    assert record['validation_calls'] == len(losses)


def check_initializer(paths, released_path, blocks):
    records = [read(path) for path in paths]
    for record in records:
        runs = record['runs']
        for run in runs:
            check_selection(run, False)
        winner = min(runs, key=lambda run: run['val'])
        assert winner['controls'] == record['selected_controls']
    fitted = AffineInitializer.fit(
        [record['descriptor'] for record in records],
        [Controls(**record['selected_controls']) for record in records], ridge=1.)
    released = AffineInitializer.load(released_path)
    assert fitted.blocks == released.blocks == blocks
    for name in ['mean', 'scale', 'W', 'bias']:
        assert np.allclose(getattr(fitted, name), getattr(released, name), atol=1e-10, rtol=1e-10), name
    return sum(len(record['runs']) for record in records)


def main(args):
    root = Path(args.root)
    forecast_sources = sorted((root/'suite').glob('calibration_*_*.json'))
    assert len(forecast_sources) == 8
    source_trials = check_initializer(forecast_sources, root/'suite/initializer.json', 2)
    assert source_trials == 128
    class_sources = sorted((root/'classification').glob('source_*.json'))
    assert len(class_sources) == 6
    class_trials = check_initializer(class_sources, root/'classification/initializer.json', 3)
    assert class_trials == 48

    data = read(root/'classification/data.json')
    train_subjects = set(data['train_subjects'])
    validation_subjects = set(data['validation_subjects'])
    # Official UCI HAR test subjects, also checked against the downloaded labels.
    import io
    import zipfile
    archive = zipfile.ZipFile(Path(args.data)/'har.zip')
    inner = [name for name in archive.namelist() if name.endswith('UCI HAR Dataset.zip')]
    if inner:
        archive = zipfile.ZipFile(io.BytesIO(archive.read(inner[0])))
    name = [name for name in archive.namelist() if name.endswith('test/subject_test.txt') and not name.startswith('__MACOSX')]
    assert len(name) == 1
    test_subjects = set(np.loadtxt(io.BytesIO(archive.read(name[0])), dtype=int).tolist())
    assert not (train_subjects & validation_subjects or train_subjects & test_subjects or validation_subjects & test_subjects)
    for path in class_sources:
        record = read(path)
        tr, va = set(record['source_train_subjects']), set(record['source_validation_subjects'])
        assert not tr & va and tr | va == train_subjects

    selection_candidates = 0
    selections = [(path, 'candidates', 15) for path in (root/'suite').glob('baseline_selection_*.json')]
    selections += [(path, 'candidates', 5) for path in (root/'convex_zero').glob('roam_selection_*.json')]
    selections += [(path, 'eligible_candidates', 5) for path in (root/'convex_zero').glob('selection_*.json')]
    selections += [(root/'classification/adamw_selection.json', 'runs', 4)]
    assert len(selections) == 16
    for path, key, count in selections:
        selection = read(path)
        runs = selection[key]
        assert len(runs) == count
        for run in runs:
            check_selection(run, False)
            assert run['seed'] == 2027
        winner = min(runs, key=lambda run: run['val'])
        assert winner['lr'] == selection['lr']
        if 'weight_decay' in selection:
            assert winner['weight_decay'] == selection['weight_decay']
        selection_candidates += len(runs)

    populations = list((root/'suite').glob('target_*.json'))
    populations += [path for path in (root/'classification').glob('target_*.json') if 'adamw' not in path.name]
    populations += list((root/'coldstart').glob('*_seed*.json'))
    assert len(populations) == 166
    direct_populations = 0
    cap_overruns = []
    search_caps = []
    cold_trials = 0
    for path in populations:
        record = read(path)
        check_selection(record, True)
        assert record['population'] == 4 and record['validation_calls'] == 20
        assert len({item['step'] for item in record['history']}) == 5
        if record['arm'] == 'direct_search':
            initial = record['initial_control_candidates']
            assert len(initial) == 4
            for member, item in enumerate(record['history'][:4]):
                assert item['member'] == member and item['controls'] == initial[member]
            direct_populations += 1
        cap_overruns.append(record['seconds'] - record['wall_seconds_cap'])
        if 'target_search_runs' in record:
            trials = record['target_search_runs']
            for run in trials:
                check_selection(run, False)
            assert record['initial_controls'] == min(trials, key=lambda run: run['val'])['controls']
            assert record['target_search_validation_calls'] == sum(run['validation_calls'] for run in trials)
            assert record['target_search_validation_calls'] <= record['source_calibration_validation_calls_cap']
            assert abs(record['target_search_seconds'] - sum(run['seconds'] for run in trials)) < 1e-9
            search_caps.append(record['target_search_seconds'] - record['source_calibration_seconds_cap'])
            cold_trials += len(trials)
    assert direct_populations == 30

    reporting = list((root/'suite').glob('convex_*.json')) + list((root/'convex_zero').glob('*_seed*.json'))
    reporting += list((root/'classification').glob('target_adamw_seed*.json'))
    assert len(reporting) == 310
    for path in reporting:
        record = read(path)
        check_selection(record, True)
        if path.parent.name == 'convex_zero':
            assert record['weight_decay'] == 0.

    report = {
        'status': 'passed', 'forecast_calibration_trials': source_trials,
        'classification_calibration_trials': class_trials,
        'initializers_recomputed': 2, 'population_records': len(populations),
        'direct_initial_populations_verified': direct_populations,
        'fixed_update_reporting_records': len(reporting), 'cold_search_trials': cold_trials,
        'learning_rate_selection_records': selection_candidates,
        'reused_reporting_records': sum('reused_from' in read(path) for path in reporting),
        'classification_subjects': {'train': sorted(train_subjects), 'validation': sorted(validation_subjects), 'test': sorted(test_subjects)},
        'maximum_final_population_evaluation_overrun_seconds': max(cap_overruns),
        'largest_search_minus_source_time_cap_seconds': max(search_caps),
        'notes': ['Selection minima and validation call counts checked for all listed records.',
                  'Run records may reuse identical fixed-update configurations; reused_from identifies these.',
                  'Time caps are scheduling thresholds; the final evaluation completes after the threshold.'],
    }
    (root/'record_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='results')
    parser.add_argument('--data', default='data')
    main(parser.parse_args())
