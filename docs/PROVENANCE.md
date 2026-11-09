# Executed and released core source

Run records retain the SHA-256 of the numerical core used for execution. That exact source is archived under `provenance/recorded_core/roam`.

After all experiments and checkpoint checks completed, one docstring in `roam/train.py` was corrected to describe the existing time-spaced validation schedule. No executable statement changed: the parsed Python ASTs are identical after removing docstrings. `provenance/release.json` records both hashes, the per-file archived hashes, and that comparison. Raw result hashes are unchanged.
