#!/bin/bash
# =============================================================================
# submit_xlm_v_validation.sh — PBS batch script for XLM-V Base zero-shot on
# the reserved 03_validation_15_cleaned splits (GPU job).
#
# Companion to submit_cross_benchmark_validation.sh (which covers the trained
# configurations + CPU off-the-shelf models). Mirrors the GPU resources of
# model_benchmarking_evaluation/xlm_v_base/submit_test_job.sh and reuses its
# test script with env-var path overrides.
# =============================================================================

# -- Resources (same as the evaluation-side XLM-V job) --------------------------
#PBS -l select=1:ncpus=4:ngpus=1:mem=16gb:Qlist=ee
#PBS -l walltime=48:00:00
#PBS -q ee

# -- Identity and Notifications -----------------------------------------------
#PBS -N xlm_v_base_VALIDATION
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/xlm_v_base_VALIDATION.out

set -e
umask 0077

REPO_ROOT="/home/25167626/LID_Experiments"
TMP="/scratch-large-network/${PBS_JOBID}"
VAL_DIR="model_benchmarking_validation"

echo "============================================================"
echo "Job:     ${PBS_JOBID}"
echo "Host:    $(hostname)"
echo "Started: $(date)"
echo "============================================================"

mkdir -p "${TMP}"

echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='datasets/03_validation_15_cleaned/librispeech_asr' \
    "${REPO_ROOT}/" "${TMP}/"

eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

export LID_BENCH_DIR="${TMP}/datasets/03_validation_15_cleaned"
export LID_OUTPUT_DIR="${TMP}/${VAL_DIR}/xlm_v_base"
mkdir -p "${LID_OUTPUT_DIR}"

echo "Running XLM-V Base zero-shot on validation splits..."
cd "${TMP}/model_benchmarking_evaluation/xlm_v_base"
python -u test_xlm_v_base_benchmark.py 2>&1 | tee "${TMP}/${VAL_DIR}/xlm_v_validation_run.log"
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: test_xlm_v_base_benchmark.py exited with code ${BENCH_EXIT}."
    /usr/bin/rsync -ax "${TMP}/${VAL_DIR}/" "${REPO_ROOT}/${VAL_DIR}/" || true
    exit ${BENCH_EXIT}
fi

echo "Syncing results back..."
/usr/bin/rsync -ax "${TMP}/${VAL_DIR}/" "${REPO_ROOT}/${VAL_DIR}/"
SYNC_EXIT=$?

if [ ${SYNC_EXIT} -eq 0 ]; then
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed (exit ${SYNC_EXIT}). Files preserved in ${TMP}."
fi

echo "Job finished: $(date)"
