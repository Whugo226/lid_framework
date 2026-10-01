#!/bin/bash
# =============================================================================
# submit_cross_benchmark_validation.sh — PBS batch script for the confirmatory
# validation-split cross-benchmark (CPU part).
#
# Evaluates every trained LID model (FastText, Logistic Regression, Naive
# Bayes) plus the CPU off-the-shelf models (CLD3, FastText lid.176) against
# every 03_validation_15_cleaned dataset — the reserved validation splits.
# Reuses hpc_cross_benchmark.py from model_benchmarking_evaluation/ with the
# validation config; no code is duplicated.
#
# XLM-V Base requires a GPU node — submit submit_xlm_v_validation.sh
# separately after (or in parallel with) this job.
#
# Checkpoint recovery: any (model, dataset) pair whose benchmark_metadata.json
# already exists is silently skipped. Re-submit on timeout:
#   qsub submit_cross_benchmark_validation.sh
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=4:mem=32gb
#PBS -l walltime=72:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N lid_cross_benchmark_validation
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/lid_cross_benchmark_validation.out

set -e
umask 0077

REPO_ROOT="/home/25167626/LID_Experiments"
TMP="/scratch-large-network/${PBS_JOBID}"
VAL_DIR="model_benchmarking_validation"

echo "============================================================"
echo "Job:     ${PBS_JOBID}"
echo "Host:    $(hostname)"
echo "Started: $(date)"
echo "Scratch: ${TMP}"
echo "============================================================"

mkdir -p "${TMP}"
if [ ! -d "${TMP}" ]; then
    echo "ERROR: Could not create scratch directory at ${TMP}."
    exit 1
fi

# Stage the repo to scratch. librispeech_asr is outside the 17-dataset
# portfolio — exclude it so no runner can pick it up by accident.
echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='datasets/03_validation_15_cleaned/librispeech_asr' \
    "${REPO_ROOT}/" "${TMP}/"

mkdir -p "${TMP}/${VAL_DIR}"

# Conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OMP_NUM_THREADS=4

# ── Part 1: trained configurations (6 configs x 17 training x 17 validation) ──
cd "${TMP}/${VAL_DIR}"
echo "Working directory: $(pwd)"

export LID_TRAINING_RESULTS_DIR="${TMP}/model_training_results"
export LID_EVAL_DATA_DIR="${TMP}/datasets/03_validation_15_cleaned"
export LID_BENCHMARK_EVAL_DIR="${TMP}/${VAL_DIR}"

echo "Starting validation-split cross-benchmark (trained configurations)..."
python -u "${TMP}/model_benchmarking_evaluation/hpc_cross_benchmark.py" \
    --config "${TMP}/${VAL_DIR}/config_cross_benchmark_validation.yaml" \
    2>&1 | tee cross_benchmark_validation_run.log
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: hpc_cross_benchmark.py exited with code ${BENCH_EXIT}."
    /usr/bin/rsync -ax "${TMP}/${VAL_DIR}/" "${REPO_ROOT}/${VAL_DIR}/" || true
    exit ${BENCH_EXIT}
fi

# ── Part 2: CPU off-the-shelf models (CLD3, FastText lid.176) ────────────────
# Reuses each family's existing test script with env-var path overrides
# (LID_BENCH_DIR → validation data, LID_OUTPUT_DIR → this directory).
export LID_BENCH_DIR="${TMP}/datasets/03_validation_15_cleaned"

echo "Running CLD3 zero-shot on validation splits..."
export LID_OUTPUT_DIR="${TMP}/${VAL_DIR}/cld3"
mkdir -p "${LID_OUTPUT_DIR}"
( cd "${TMP}/model_benchmarking_evaluation/cld3" && \
  python -u test_cld3_benchmark.py ) 2>&1 | tee -a cross_benchmark_validation_run.log

echo "Running FastText lid.176 zero-shot on validation splits..."
export LID_OUTPUT_DIR="${TMP}/${VAL_DIR}/fasttext_off_the_shelf"
mkdir -p "${LID_OUTPUT_DIR}"
( cd "${TMP}/model_benchmarking_evaluation/fasttext_off_the_shelf" && \
  python -u test_fasttext_offtheshelf_benchmark.py ) 2>&1 | tee -a cross_benchmark_validation_run.log

# ── Sync results back ─────────────────────────────────────────────────────────
echo "Benchmarks complete. Syncing results back..."
/usr/bin/rsync -ax "${TMP}/${VAL_DIR}/" "${REPO_ROOT}/${VAL_DIR}/"
SYNC_EXIT=$?

if [ ${SYNC_EXIT} -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed (exit ${SYNC_EXIT}). Files preserved in ${TMP}."
fi

echo "============================================================"
echo "Job finished: $(date)"
echo "============================================================"
