#!/bin/bash
# =============================================================================
# submit_cross_benchmark.sh — PBS batch script for hpc_cross_benchmark.py
#
# Evaluates every trained LID model (FastText, Logistic Regression, Naive Bayes)
# against every evaluation dataset, producing the full N×M cross-dataset
# benchmark matrix needed to populate Rec score / Δ in validate_recommendations.py.
#
# Checkpoint recovery: any (model, eval_dataset) pair whose
# benchmark_metadata.json already exists is silently skipped.  If the job
# times out, re-submit with:
#   qsub submit_cross_benchmark.sh
#
# Resource rationale:
#   4 CPUs — sklearn vectorizer uses n_jobs=-1; FastText is single-threaded.
#   32 GB  — one FastText model (~339 MB) + one eval dataset (~200 MB) at a time;
#            sklearn pipelines are much smaller.
#   72 h   — full matrix (~1,632 new pairs) runs in ~2 h; 72 h gives ample
#            headroom and allows checkpoint recovery across submissions.
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=4:mem=32gb
#PBS -l walltime=72:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N lid_cross_benchmark
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/lid_cross_benchmark.out

# =============================================================================
# Execution with Network Scratch Space
# =============================================================================

set -e
umask 0077

# 1. Define paths
REPO_ROOT="/home/25167626/LID_Experiments"
TMP="/scratch-large-network/${PBS_JOBID}"

echo "============================================================"
echo "Job:     ${PBS_JOBID}"
echo "Host:    $(hostname)"
echo "Started: $(date)"
echo "Scratch: ${TMP}"
echo "============================================================"

# 2. Create scratch workspace
mkdir -p "${TMP}"
if [ ! -d "${TMP}" ]; then
    echo "ERROR: Could not create scratch directory at ${TMP}."
    exit 1
fi

# 3. Stage the entire LID_Experiments repo to scratch
#    (includes renamed variant dirs from migrate_eval_dirs.py — these act as
#     the checkpoint; hpc_cross_benchmark.py skips any pair already present)
echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "${REPO_ROOT}/" "${TMP}/"

# 4. Navigate to the benchmark evaluation dir inside scratch
cd "${TMP}/model_benchmarking_evaluation"
echo "Working directory: $(pwd)"

# 5. Activate conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 6. Thread-limit overrides (prevent OpenBLAS/MKL from spawning excessive threads)
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OMP_NUM_THREADS=4

# 7. Export path overrides — point all I/O to scratch
export LID_TRAINING_RESULTS_DIR="${TMP}/model_training_results"
export LID_EVAL_DATA_DIR="${TMP}/datasets/02_evaluation_15_cleaned"
export LID_BENCHMARK_EVAL_DIR="${TMP}/model_benchmarking_evaluation"

# 8. Run the cross-benchmark script with unbuffered output
echo "Starting cross-dataset benchmark (full N×M matrix)..."
python -u hpc_cross_benchmark.py 2>&1 | tee cross_benchmark_run.log
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: hpc_cross_benchmark.py exited with code ${BENCH_EXIT}."
    echo "Syncing logs back before exiting..."
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_evaluation/cross_benchmark_run.log" \
        "${REPO_ROOT}/model_benchmarking_evaluation/"
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_evaluation/cross_benchmark.log" \
        "${REPO_ROOT}/model_benchmarking_evaluation/" 2>/dev/null || true
    exit ${BENCH_EXIT}
fi

# 9. Sync new benchmark results back to permanent storage
#    Only syncs model_benchmarking_evaluation/ — not the raw data or models.
echo "Benchmark complete. Syncing results back..."
/usr/bin/rsync -ax \
    "${TMP}/model_benchmarking_evaluation/" \
    "${REPO_ROOT}/model_benchmarking_evaluation/"

SYNC_EXIT=$?

# 10. Cleanup scratch ONLY if sync succeeded
if [ ${SYNC_EXIT} -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed (exit ${SYNC_EXIT}). Files preserved in ${TMP} for manual recovery."
fi

echo "============================================================"
echo "Job finished: $(date)"
echo "============================================================"
