#!/bin/bash
# =============================================================================
# submit_job.sh — PBS batch script for hpc_build_mkb.py
#
# Profiles up to 17 historical datasets using DeepProfiler (building mode),
# then assembles the Meta-Knowledge Base (MKBStore) from those profiles plus
# the model benchmarking results already on disk.
#
# Checkpoint recovery: The script uses a skip-if-exists mechanism — any dataset
# whose .pkl already exists in profiles/ is silently skipped. If the job times
# out before all 17 datasets are processed, simply re-submit with:
#   qsub submit_job.sh
# Each re-submission resumes from where the previous job stopped. Expect 2–3
# submissions of 72 h each for the full 17-dataset run.
#
# Resource rationale:
#   DeepProfiler is CPU-bound (spaCy NLP pipeline). 8 CPUs give headroom for
#   spaCy's internal tokeniser and OS overhead. Memory does NOT scale with
#   dataset count — only one dataset directory is loaded at a time, so 128 GB
#   covers the same per-dataset footprint as before: up to 24 spaCy models
#   (~200 MB each), the FastText LID model (~1 GB), 24 compressed FastText
#   word-vector models (~100–300 MB each), and working DataFrames. Walltime is
#   72 h per submission; checkpoint recovery handles the remaining datasets in
#   subsequent submissions.
# =============================================================================

# -- Resources ----------------------------------------------------------------
#PBS -l select=1:ncpus=8:mem=128gb
#PBS -l walltime=72:00:00

# -- Identity and Notifications -----------------------------------------------
#PBS -N lid_build_mkb
#PBS -M 25167626@sun.ac.za
#PBS -m abe

# -- Output / error logs ------------------------------------------------------
#PBS -j oe
#PBS -o /home/25167626/jobs/lid_build_mkb.out

# =============================================================================
# Execution with Network Scratch Space
# =============================================================================

# 1. Secure the environment
set -e
umask 0077

# 2. Define paths
TOOLKIT_ROOT="/home/25167626/lid_toolkit"     # where this repo lives on HPC
LID_ROOT="/home/25167626/LID_Experiments"     # datasets and benchmarking results
TMP="/scratch-large-network/${PBS_JOBID}"     # fast network scratch

# Persistent caches that survive between jobs (never on scratch)
FT_CACHE="/home/25167626/.cache/lid_toolkit/fasttext_cache"
PROFILES_DIR="${TOOLKIT_ROOT}/profiles"       # .pkl outputs synced back after job

echo "============================================================"
echo "Job:        ${PBS_JOBID}"
echo "Host:       $(hostname)"
echo "Started:    $(date)"
echo "Scratch:    ${TMP}"
echo "============================================================"

# 3. Create scratch workspace
mkdir -p "${TMP}"
if [ ! -d "${TMP}" ]; then
    echo "ERROR: Could not create scratch directory at ${TMP}."
    exit 1
fi

# 4. Ensure persistent cache directory exists
mkdir -p "${FT_CACHE}"

# 5. Stage the toolkit to scratch (fast local copy avoids NFS contention)
echo "Staging lid_toolkit to scratch..."
/usr/bin/rsync -ax \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='fasttext_cache' \
    --exclude='profiles' \
    "${TOOLKIT_ROOT}/" "${TMP}/"

# 6. Symlink the persistent fasttext_cache into the scratch CWD so that
#    DeepProfiler._load_fasttext_model (which writes to ./fasttext_cache)
#    actually writes to permanent storage and the models survive between jobs.
ln -sfn "${FT_CACHE}" "${TMP}/fasttext_cache"

# 7. Stage any existing .pkl profiles into scratch so the skip-if-exists
#    checkpoint in profile_and_save_historical can skip completed datasets.
if [ -d "${PROFILES_DIR}" ]; then
    echo "Copying existing profiles to scratch (checkpoint recovery)..."
    mkdir -p "${TMP}/profiles"
    /usr/bin/rsync -ax "${PROFILES_DIR}/" "${TMP}/profiles/"
fi

# 8. Navigate to toolkit root inside scratch
cd "${TMP}"
echo "Working directory: $(pwd)"

# 9. Activate conda and install the staged toolkit
eval "$(/home/apps2/miniconda3/bin/conda shell.bash hook)"
conda activate thesis_final
echo "Using Python: $(which python)"

pip install -e . --quiet

# 10. Pre-download spaCy models (inside the job where thread limits are higher)
#     Skip if all models are already installed (idempotent)
echo "Downloading spaCy language models (this may take 10–15 minutes on first run)..."
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1

python << 'SPACY_DOWNLOAD'
import spacy
import sys

models = {
    'en': 'en_core_web_sm', 'ca': 'ca_core_news_sm', 'zh': 'zh_core_web_sm',
    'hr': 'hr_core_news_sm', 'da': 'da_core_news_sm', 'nl': 'nl_core_news_sm',
    'fi': 'fi_core_news_sm', 'fr': 'fr_core_news_sm', 'de': 'de_core_news_sm',
    'el': 'el_core_news_sm', 'it': 'it_core_news_sm',
    'ko': 'ko_core_news_sm', 'lt': 'lt_core_news_sm', 'mk': 'mk_core_news_sm',
    'nb': 'nb_core_news_sm', 'pl': 'pl_core_news_sm', 'pt': 'pt_core_news_sm',
    'ro': 'ro_core_news_sm', 'ru': 'ru_core_news_sm', 'sl': 'sl_core_news_sm',
    'es': 'es_core_news_sm', 'sv': 'sv_core_news_sm', 'uk': 'uk_core_news_sm',
}
# Note: 'ja' (Japanese) uses ja-ginza, which is installed via pip/conda, not spacy.cli.download()

failed = []
for lang, model_name in models.items():
    if spacy.util.is_package(model_name):
        print(f'  ✓ {model_name}')
    else:
        try:
            print(f'  ⬇ Downloading {model_name}...')
            spacy.cli.download(model_name)
            # Verify the download actually succeeded (spacy.cli.download may not raise on failure)
            if not spacy.util.is_package(model_name):
                raise RuntimeError(f'{model_name} not installed after download attempt')
        except Exception as e:
            print(f'  ✗ Failed to download {model_name}: {e}')
            failed.append(model_name)

if failed:
    print(f'\nWarning: Failed to download {len(failed)} model(s): {failed}')
    print('DeepProfiler will skip these languages.')
    sys.exit(0)  # Don't abort; profiling can continue with available models

print('\n✓ All spaCy models ready.')
SPACY_DOWNLOAD

echo "spaCy models download complete."

# 11. Run the MKB build script with unbuffered output
#     Config env-var overrides so paths point to the right locations.
export LID_DATASETS_ROOT="${LID_ROOT}/datasets/01b_knowledge_benchmark_20_cleaned"
export LID_PROFILES_DIR="${TMP}/profiles"
export LID_BENCHMARK_DIR="${LID_ROOT}/model_benchmarking"
export LID_MKB_OUTPUT="${TMP}/mkb.pkl"

echo "Starting MKB build (6 datasets)..."
python -u hpc_build_mkb.py --config config.yaml 2>&1 | tee build_mkb.log
BUILD_EXIT=${PIPESTATUS[0]}

if [ ${BUILD_EXIT} -ne 0 ]; then
    echo "ERROR: hpc_build_mkb.py exited with code ${BUILD_EXIT}."
    echo "Syncing logs back for inspection before exiting..."
    /usr/bin/rsync -ax "${TMP}/build_mkb.log" "${TOOLKIT_ROOT}/"
    exit ${BUILD_EXIT}
fi

# 12. Sync results back to permanent storage
echo "Build complete. Syncing results back..."
mkdir -p "${PROFILES_DIR}"

# Sync profile .pkl files back
/usr/bin/rsync -ax "${TMP}/profiles/" "${PROFILES_DIR}/"

# Sync the finished MKBStore
/usr/bin/rsync -ax "${TMP}/mkb.pkl"       "${TOOLKIT_ROOT}/"
/usr/bin/rsync -ax "${TMP}/build_mkb.log" "${TOOLKIT_ROOT}/"

SYNC_EXIT=$?

# 13. Cleanup scratch ONLY if sync succeeded
if [ ${SYNC_EXIT} -eq 0 ]; then
    echo "Sync successful. Cleaning up scratch space."
    /bin/rm -rf "${TMP}"
else
    echo "Warning: Sync failed (exit ${SYNC_EXIT}). Files preserved in ${TMP} for manual recovery."
fi

echo "============================================================"
echo "Job finished: $(date)"
echo "============================================================"
