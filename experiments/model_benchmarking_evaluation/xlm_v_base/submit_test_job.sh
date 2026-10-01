#!/bin/bash
# =============================================================================
# submit_test_job.sh — PBS batch script for xlm-v-base-language-id
#                      evaluation benchmark (02 datasets)
#
# Evaluates juliensimon/xlm-v-base-language-id against all 17 02_evaluation
# datasets. Results feed into validate_recommendations.py as ground-truth
# performance data for the xlm_v_base_language_id variant key.
#
# Run AFTER the knowledge benchmark (submit_test_job.sh in xlm_v_base/) and
# after rebuilding the MKB. Both benchmarks share the same variant_name
# ("xlm_v_base_language_id") so the validate script can resolve scores.
#
# Checkpoint recovery: datasets whose benchmark_metadata.json already exists
# are skipped. Re-submit with qsub to resume after a timeout.
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=4:ngpus=1:mem=16gb:Qlist=ee
#PBS -l walltime=48:00:00

# -- Queue --------------------------------------------------------------------
#PBS -q ee

# -- Identity and Notifications -----------------------------------------------
#PBS -N xlm_v_base_EVAL
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/xlm_v_base_EVAL.out

# =============================================================================
# Execution
# =============================================================================

set -e
umask 0077

REPO_ROOT="/home/25167626/LID_Experiments"
TMP="/scratch-large-network/${PBS_JOBID}"

echo "============================================================"
echo "Job:     ${PBS_JOBID}"
echo "Host:    $(hostname)"
echo "Started: $(date)"
echo "Scratch: ${TMP}"
echo "============================================================"

# 1. Create scratch workspace
mkdir -p "${TMP}"
if [ ! -d "${TMP}" ]; then
    echo "ERROR: Could not create scratch directory at ${TMP}."
    exit 1
fi

# 2. Stage project to scratch
echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "${REPO_ROOT}/" "${TMP}/"

# 3. Navigate to script directory inside scratch
cd "${TMP}/model_benchmarking_evaluation/xlm_v_base"
echo "Working directory: $(pwd)"

# 4. Activate conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 5. Point HuggingFace cache to scratch
export TRANSFORMERS_CACHE="${TMP}/.cache/huggingface"
export HF_HOME="${TMP}/.cache/huggingface"
mkdir -p "${TRANSFORMERS_CACHE}"

# 6. Thread-limit overrides
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OMP_NUM_THREADS=4

# 7. Override I/O paths to scratch
export LID_BENCH_DIR="${TMP}/datasets/02_evaluation_15_cleaned"
export LID_OUTPUT_DIR="${TMP}/model_benchmarking_evaluation/xlm_v_base"

# 8. Run benchmark
echo "Starting xlm-v-base-language-id evaluation benchmark (17 datasets)..."
python -u test_xlm_v_base_benchmark.py 2>&1 | tee benchmark_run.log
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: benchmark exited with code ${BENCH_EXIT}. Syncing logs before exit..."
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_evaluation/xlm_v_base/benchmark_run.log" \
        "${REPO_ROOT}/model_benchmarking_evaluation/xlm_v_base/" 2>/dev/null || true
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_evaluation/xlm_v_base/benchmark.log" \
        "${REPO_ROOT}/model_benchmarking_evaluation/xlm_v_base/" 2>/dev/null || true
    exit ${BENCH_EXIT}
fi

# 9. Sync results back to permanent storage
echo "Benchmark complete. Syncing results back..."
/usr/bin/rsync -ax \
    "${TMP}/model_benchmarking_evaluation/xlm_v_base/" \
    "${REPO_ROOT}/model_benchmarking_evaluation/xlm_v_base/"
SYNC_EXIT=$?

# 10. Cleanup scratch only if sync succeeded
if [ ${SYNC_EXIT} -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed (exit ${SYNC_EXIT}). Files preserved in ${TMP} for manual recovery."
fi

echo "============================================================"
echo "Job finished: $(date)"
echo "============================================================"
