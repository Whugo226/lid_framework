# Confirmatory Validation Run (03_validation_15_cleaned)

One-shot confirmatory evaluation of the framework on the reserved validation
splits, under the frozen protocol of the recorded evaluation run
(k=3, f1_weighted, coverage guard inactive, seed 42, 500 texts/language).

`librispeech_asr` exists in `03_validation_15_cleaned` but is outside the
17-dataset portfolio — it is excluded from the config and from the rsync
staging in both submit scripts.

## Order of operations

1. **HPC — ground-truth cross-benchmark (two jobs, can run in parallel):**

   ```sh
   qsub submit_cross_benchmark_validation.sh   # trained configs + CLD3 + lid.176 (CPU)
   qsub submit_xlm_v_validation.sh             # XLM-V Base (GPU, queue ee)
   ```

   Both reuse the existing runners from `model_benchmarking_evaluation/`
   (no code duplicated): the trained-config matrix runs through
   `hpc_cross_benchmark.py --config config_cross_benchmark_validation.yaml`;
   the off-the-shelf models run through their own `test_*_benchmark.py`
   scripts with `LID_BENCH_DIR`/`LID_OUTPUT_DIR` env overrides.
   Checkpoint recovery: re-submit on timeout; finished pairs are skipped.

2. **Sync `model_benchmarking_validation/` back to this machine** (same
   OneDrive/rsync flow as the evaluation-side results).

3. **Local — one-shot framework run:**

   ```sh
   cd ../../Python/toolkit_dev/lid_toolkit
   python validate_recommendations_validation.py
   ```

   The script pre-flights that every dataset has benchmark metadata, refuses
   to overwrite an existing `validation_confirmatory_report.json`, and writes
   its own log/cache files (nothing from the recorded evaluation run is
   touched).

4. **Baselines on the validation report (local, after step 3):**

   ```sh
   python analysis/random_baseline_mc.py --report validation_confirmatory_report.json
   python analysis/llm_baseline.py --report validation_confirmatory_report.json \
       --eval-dir ../../..//LID_experiments/datasets/03_validation_15_cleaned
   ```

   (`llm_baseline.py` needs `ANTHROPIC_API_KEY` and internet — local only.)

## Protocol freeze

The protocol constants are hard-coded in
`validate_recommendations_validation.py` (no CLI overrides) and were fixed
before any validation-split ground truth was inspected. The run is intended
to be executed exactly once; its results go into the thesis as-is.

## Verify before first submit

- The OTS env-override names (`LID_BENCH_DIR`, `LID_OUTPUT_DIR`) were
  confirmed in `cld3/test_cld3_benchmark.py` and
  `xlm_v_base/test_xlm_v_base_benchmark.py`; spot-check
  `fasttext_off_the_shelf/test_fasttext_offtheshelf_benchmark.py` uses the
  same keys before submitting.
- Confirm `hpc_cross_benchmark.py --config` is supported on the HPC copy of
  the repo (added via `--config` CLI arg; present in the current version).
