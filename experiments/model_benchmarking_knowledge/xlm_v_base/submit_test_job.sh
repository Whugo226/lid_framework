#!/bin/bash
# =============================================================================
# submit_test_job.sh — PBS batch script for xlm-v-base-language-id
#                      knowledge benchmark (01b datasets)
#
# Downloads juliensimon/xlm-v-base-language-id from HuggingFace Hub on first
# run and caches it to scratch. Results go to model_benchmarking_knowledge/xlm_v_base/
# and are synced back to permanent storage on completion.
#
# Checkpoint recovery: datasets whose benchmark_metadata.json already exists
# are skipped. Re-submit with qsub to resume after a timeout.
#
# Resource rationale:
#   1 GPU  — transformer inference; batch_size=32 fits on 16 GB VRAM.
#   4 CPUs — DataLoader + I/O; num_workers=0 (fork-safe on HPC).
#   32 GB  — model weights (~1.1 GB) + largest eval set (multilingual_cc_news ~4 GB).
#   48 h   — 18 datasets × ~15 min each = ~4.5 h; 48 h gives full headroom.
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=4:ngpus=1:mem=16gb:Qlist=ee
#PBS -l walltime=48:00:00

# -- Queue --------------------------------------------------------------------
#PBS -q ee

# -- Identity and Notifications -----------------------------------------------
#PBS -N xlm_v_base_knowledge
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/xlm_v_base_knowledge.out

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

# 2. Stage project to scratch (excludes mlruns and git history)
echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "${REPO_ROOT}/" "${TMP}/"

# 3. Navigate to script directory inside scratch
cd "${TMP}/model_benchmarking_knowledge/xlm_v_base"
echo "Working directory: $(pwd)"

# 4. Activate conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 5. Point HuggingFace cache to scratch so model download doesn't fill home quota
export TRANSFORMERS_CACHE="${TMP}/.cache/huggingface"
export HF_HOME="${TMP}/.cache/huggingface"
mkdir -p "${TRANSFORMERS_CACHE}"

# 6. Thread-limit overrides
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OMP_NUM_THREADS=4

# 7. Override I/O paths to scratch
export LID_BENCH_DIR="${TMP}/datasets/01b_knowledge_benchmark_20_cleaned"
export LID_OUTPUT_DIR="${TMP}/model_benchmarking_knowledge/xlm_v_base"

# 8. Run benchmark
echo "Starting xlm-v-base-language-id knowledge benchmark (18 datasets)..."
python -u test_xlm_v_base_benchmark.py 2>&1 | tee benchmark_run.log
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: benchmark exited with code ${BENCH_EXIT}. Syncing logs before exit..."
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_knowledge/xlm_v_base/benchmark_run.log" \
        "${REPO_ROOT}/model_benchmarking_knowledge/xlm_v_base/" 2>/dev/null || true
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_knowledge/xlm_v_base/benchmark.log" \
        "${REPO_ROOT}/model_benchmarking_knowledge/xlm_v_base/" 2>/dev/null || true
    exit ${BENCH_EXIT}
fi

# 9. Sync results back to permanent storage
echo "Benchmark complete. Syncing results back..."
/usr/bin/rsync -ax \
    "${TMP}/model_benchmarking_knowledge/xlm_v_base/" \
    "${REPO_ROOT}/model_benchmarking_knowledge/xlm_v_base/"
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
