#!/bin/bash
# =============================================================================
# submit_test_job.sh — PBS batch script for test_fasttext_offtheshelf_benchmark.py
#
# Benchmarks the pre-trained FastText LID model (lid.176.bin) against the
# held-out benchmark data. FastText inference is lightweight (single C++ pass,
# no sparse-matrix transforms) — 16 GB and 2 hours covers all 6 datasets.
# =============================================================================

# -- Resources ----------------------------------------------------------------
# 4 CPUs available for data loading; FastText inference itself is single-threaded
# but benefits from available cores during parquet I/O. 32 GB is sufficient for
# the full benchmark corpus (17 datasets) with FastText's compact in-memory model.
#PBS -l select=1:ncpus=4:mem=32gb
#PBS -l walltime=08:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N fasttext_ots_lid_benchmark_EVAL
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
# Join stdout and stderr into one file in your home directory.
#PBS -j oe
#PBS -o /home/25167626/jobs/fasttext_ots_lid_benchmark_EVAL.out

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
echo "Staging project files to scratch..."
/usr/bin/rsync -vax \
    --exclude='mlruns' \
    --exclude='.git' \
    "${REPO_ROOT}/" "${TMP}/"

# 5. Navigate to the benchmark script location inside scratch
cd "${TMP}/model_benchmarking_evaluation/fasttext_off_the_shelf"
echo "Working directory: $(pwd)"

# 6. Activate the conda environment
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

# 7. Set environment variable overrides so the script resolves all paths
#    to the scratch copies (avoids NFS latency during inference).
export LID_MODEL_PATH="${TMP}/off_the_shelf_models/fasttext/lid.176.bin"
export LID_BENCH_DIR="${TMP}/datasets/02_evaluation_15_cleaned"
export LID_OUTPUT_DIR="${TMP}/model_benchmarking_evaluation/fasttext_off_the_shelf"

# 8. Run the benchmark with unbuffered output
# -u ensures progress is visible via 'qpeek' while the job is running.
echo "Starting FastText off-the-shelf benchmark (17 datasets × 1 model)..."
python -u test_fasttext_offtheshelf_benchmark.py

# 9. Sync results back to the permanent home directory
# Only the output subdirectory is synced — model weights and raw data stay on scratch.
echo "Benchmark finished. Syncing results back to permanent storage..."
/usr/bin/rsync -vax "${TMP}/model_benchmarking_evaluation/fasttext_off_the_shelf/" "${PBS_O_WORKDIR}/"

# 10. Cleanup: delete temporary files ONLY if rsync succeeded
if [ $? -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed. Files preserved in ${TMP} for manual recovery."
fi

echo "Job ended at $(date)"
