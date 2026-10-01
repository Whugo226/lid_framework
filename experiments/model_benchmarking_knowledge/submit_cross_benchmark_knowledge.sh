#!/bin/bash
# =============================================================================
# submit_cross_benchmark_knowledge.sh — PBS batch script for knowledge base
#                                       cross-benchmark
#
# Evaluates every trained LID model (FastText, Logistic Regression, Naive Bayes)
# against every 01b_knowledge_benchmark_20_cleaned dataset, producing the full
# N×M cross-dataset matrix needed to populate the MKB with cross-dataset
# performance data. This fixes IDW degeneracy in the recommender.
#
# Checkpoint recovery: any (model, eval_dataset) pair whose
# benchmark_metadata.json already exists is silently skipped. Re-submit with:
#   qsub submit_cross_benchmark_knowledge.sh
#
# Resource rationale:
#   4 CPUs — sklearn vectorizer uses n_jobs=-1; FastText is single-threaded.
#   32 GB  — one FastText model (~339 MB) + one eval dataset (~200 MB) at a time.
#   72 h   — full matrix (~1,944 pairs) runs in ~2 h; 72 h gives ample headroom.
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=4:mem=32gb
#PBS -l walltime=72:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N lid_cross_benchmark_knowledge
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/lid_cross_benchmark_knowledge.out

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
echo "Staging LID_Experiments to scratch..."
/usr/bin/rsync -ax \
    --exclude='mlruns' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "${REPO_ROOT}/" "${TMP}/"

# 4. Navigate to the benchmark evaluation dir (where hpc_cross_benchmark.py lives)
cd "${TMP}/model_benchmarking_evaluation"
echo "Working directory: $(pwd)"

# 5. Activate conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 6. Thread-limit overrides
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OMP_NUM_THREADS=4

# 7. Export path overrides — point all I/O to scratch
export LID_TRAINING_RESULTS_DIR="${TMP}/model_training_results"
export LID_EVAL_DATA_DIR="${TMP}/datasets/01b_knowledge_benchmark_20_cleaned"
export LID_BENCHMARK_EVAL_DIR="${TMP}/model_benchmarking_knowledge"

# 8. Run the cross-benchmark script with the knowledge config
echo "Starting knowledge cross-benchmark (full N×M matrix on 01b datasets)..."
python -u hpc_cross_benchmark.py \
    --config "${TMP}/model_benchmarking_knowledge/config_cross_benchmark_knowledge.yaml" \
    2>&1 | tee "${TMP}/model_benchmarking_knowledge/cross_benchmark_knowledge_run.log"
BENCH_EXIT=${PIPESTATUS[0]}

if [ ${BENCH_EXIT} -ne 0 ]; then
    echo "ERROR: hpc_cross_benchmark.py exited with code ${BENCH_EXIT}."
    echo "Syncing logs back before exiting..."
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_knowledge/cross_benchmark_knowledge_run.log" \
        "${REPO_ROOT}/model_benchmarking_knowledge/"
    /usr/bin/rsync -ax \
        "${TMP}/model_benchmarking_knowledge/cross_benchmark_knowledge.log" \
        "${REPO_ROOT}/model_benchmarking_knowledge/" 2>/dev/null || true
    exit ${BENCH_EXIT}
fi

# 9. Sync new benchmark results back to permanent storage
echo "Benchmark complete. Syncing results back..."
/usr/bin/rsync -ax \
    "${TMP}/model_benchmarking_knowledge/" \
    "${REPO_ROOT}/model_benchmarking_knowledge/"

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
