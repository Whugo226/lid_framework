#!/bin/bash
# =============================================================================
# submit_test_job.sh — PBS batch script for test_cld3_benchmark.py
#
# Benchmarks Google's CLD3 (gcld3 Python bindings) against the held-out
# benchmark data. CLD3 is a lightweight pre-trained neural network bundled
# inside the gcld3 package — no model files need to be staged.
# Inference is CPU-bound and single-threaded (per-sample loop); 32 GB RAM
# and 4 CPUs are sufficient for all 6 datasets.
# =============================================================================

# -- Resources ----------------------------------------------------------------
# 4 CPUs available for OS scheduling; CLD3 inference itself is single-threaded.
# 32 GB covers the full benchmark corpus loaded into pandas DataFrames.
#PBS -l select=1:ncpus=4:mem=32gb
#PBS -l walltime=12:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N cld3_lid_benchmark_EVAL
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
# Join stdout and stderr into one file in your home directory.
#PBS -j oe
#PBS -o /home/25167626/jobs/cld3_lid_benchmark_EVAL.out

# =============================================================================
# Execution with Scratch Space
# =============================================================================

# 1. Secure the environment (disallows other users access)
umask 0077

# 2. Define paths
REPO_ROOT="/home/25167626/LID_Experiments"
TMP="/scratch-large-network/${PBS_JOBID}"

echo "Job started on $(hostname) at $(date)"
echo "Targeting Network Scratch: ${TMP}"

# 3. Create the temporary workspace
mkdir -p "${TMP}"
if [ ! -d "${TMP}" ]; then
    echo "ERROR: Could not create scratch directory at ${TMP}. Path may be wrong or disk full."
    exit 1
fi

# 4. Stage the entire project to scratch.
# Excludes mlruns (large, not needed for inference) and .git.
# No model weights directory needs to be staged — CLD3 is bundled in the
# gcld3 conda package.
echo "Staging project files to scratch..."
/usr/bin/rsync -vax \
    --exclude='mlruns' \
    --exclude='.git' \
    "${REPO_ROOT}/" "${TMP}/"

# 5. Navigate to the benchmark script location inside scratch
cd "${TMP}/model_benchmarking_evaluation/cld3"
echo "Working directory: $(pwd)"

# 6. Activate the conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 7. Set environment variable overrides so the script resolves all paths
#    to the scratch copies (avoids NFS latency during inference).
#    LID_MODEL_DIR is not exported — CLD3 requires no external model file.
export LID_BENCH_DIR="${TMP}/datasets/02_evaluation_15_cleaned"
export LID_OUTPUT_DIR="${TMP}/model_benchmarking_evaluation/cld3"

# 8. Run the benchmark with unbuffered output
# -u ensures progress is visible via 'qpeek' while the job is running.
echo "Starting CLD3 benchmark (17 datasets, single model)..."
python -u test_cld3_benchmark.py

# 9. Sync results back to the permanent home directory
# Only the output subdirectory is synced — raw data stays on scratch.
echo "Benchmark finished. Syncing results back to permanent storage..."
/usr/bin/rsync -vax "${TMP}/model_benchmarking_evaluation/cld3/" "${PBS_O_WORKDIR}/"

# 10. Cleanup: delete temporary files ONLY if rsync succeeded
if [ $? -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed. Files preserved in ${TMP} for manual recovery."
fi

echo "Job ended at $(date)"
