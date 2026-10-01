# Experimental programme

These scripts produced the evidence base of the framework: the four-way
corpus splits, the 102 trained candidate models and the 1,785 cross-benchmark
records stored in `mkb.pkl`. They are copied unchanged from the author's
working folder (`LID_experiments`), so they record what was actually run.

They were run partly on a Windows workstation and partly on Stellenbosch
University's HPC1 cluster (PBS job scheduler), and they still contain the
absolute paths and job settings of those machines. To rerun them elsewhere,
edit the paths in each script and `config*.yaml` first.

No data or models are included. The corpora are downloaded from the Hugging
Face Hub (see `docs/model_card.md` for the list), and the trained models are
published at
[werner1hugo/lid-framework-models](https://huggingface.co/werner1hugo/lid-framework-models).

## Pipeline, in the order it was run

### 1. Ingest and split the corpora (`datasets/`)

| Script | What it does |
|---|---|
| `data_split_generator_with_duckdb.py` | Streams 16 of the 17 corpora from the Hugging Face Hub, truncates each document to at most 120 characters (40 for CJK) and drops those under 30 (10 for CJK), keeps only the 24 target languages, caps each language at 200,000 rows per corpus, and routes every row at random (seed 42) to one of four splits: knowledge-training 50%, knowledge-benchmarking 20%, evaluation 15%, validation 15%. Corpora that are commented out in its list were not used. |
| `ingest_europarl.py` | The same for Europarl, whose rows are translation pairs rather than plain text. It reuses the functions of the main script. |
| `data_cleaning.py` | Writes a sanitised copy of every split (`*_cleaned`): removes URLs, HTML tags and @-mentions and collapses whitespace, with no lowercasing. All later steps use the sanitised splits. |

### 2. Train the six configurations (`model_training/`)

One folder per family, each with its training script, its `config.yaml`
(data folder, sampling, cross-validation, search space and seed) and the PBS
job script used to submit it:

| Folder | Configurations |
|---|---|
| `naive_bayes/` | Multinomial Naive Bayes over character 3–5-grams, bag-of-words and TF-IDF |
| `logistic_regression/` | Logistic regression over character 3–5-grams, max-abs-scaled bag-of-words and TF-IDF |
| `fasttext/` | FastText word and FastText subword |

Each script trains on the knowledge-training split of every corpus, selects
hyperparameters by macro-F1 on an internal stratified split, and writes one
folder per model (`model.bin` or `best_pipeline.pkl`, plus `run_metadata.json`).

### 3. Cross-benchmark every candidate on every corpus

Every candidate is run on every corpus, three times: once per held-out split.

| Folder | Split | Used for |
|---|---|---|
| `model_benchmarking_knowledge/` | knowledge-benchmarking (20%) | The performance records stored in the MKB |
| `model_benchmarking_evaluation/` | evaluation (15%) | The ground truth of the held-out evaluation (thesis Chapter 5) |
| `model_benchmarking_validation/` | validation (15%) | The ground truth of the single confirmatory run |

All three use the runners in `model_benchmarking_evaluation/`:

- `hpc_cross_benchmark.py` runs the 102 trained models. The three splits
  differ only in the config file passed to it (`config_cross_benchmark*.yaml`).
- `cld3/`, `fasttext_off_the_shelf/` (lid.176) and `xlm_v_base/` run the three
  off-the-shelf detectors. XLM-V Base was run on a GPU.

`model_benchmarking_validation/README.md` describes the confirmatory run step
by step.

## Software

Besides the framework's own dependencies, these scripts need `datasets`,
`duckdb` and `pyarrow` (step 1), and `gcld3`, `transformers` and `torch` for
the CLD3 and XLM-V Base benchmarks.
