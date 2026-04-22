#!/usr/bin/env python
"""
hpc_build_mkb.py — HPC entry point for building the Meta-Knowledge Base.

Two-phase execution
-------------------
Phase 1 — Profile historical datasets
    Walks ``datasets_root``, calls DeepProfiler in building mode on every
    dataset sub-directory, and saves one .pkl per dataset to ``profiles_dir``.
    Datasets whose .pkl already exists are silently skipped (checkpoint-safe:
    re-submitting the job after a failure resumes from where it stopped).

Phase 2 — Assemble the MKBStore
    Loads all .pkl files from ``profiles_dir`` together with model benchmarking
    results from ``benchmark_dir``, fits the PCA stratifier, and serialises the
    finished MKBStore to ``mkb_output_path``.

Usage
-----
    python hpc_build_mkb.py [--config config.yaml] [--skip-phase2]

Environment-variable overrides (set in submit_job.sh)
------------------------------------------------------
    LID_DATASETS_ROOT  → paths.datasets_root
    LID_PROFILES_DIR   → paths.profiles_dir
    LID_BENCHMARK_DIR  → paths.benchmark_dir
    LID_MKB_OUTPUT     → paths.mkb_output_path
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def _resolve(cfg_value: str | None, env_var: str, base: Path) -> Path | None:
    """Return the effective path for a config entry.

    Priority: environment variable > config file value > None.
    Relative paths are resolved against *base* (the config file's directory).
    ``~`` is expanded in all cases.
    """
    raw = os.environ.get(env_var) or cfg_value
    if raw is None:
        return None
    p = Path(raw).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _setup_logging(level: str, log_file: Path | None) -> None:
    fmt = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode="a", encoding="utf-8"))
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                        format=fmt, datefmt=datefmt, handlers=handlers)


# ---------------------------------------------------------------------------
# Phase 1 — profiling
# ---------------------------------------------------------------------------

def run_phase1(
    datasets_root: Path,
    profiles_dir: Path,
    skip_datasets: list[str],
    logger: logging.Logger,
) -> int:
    """Profile all datasets and return the number of profiles written."""
    from lid_toolkit.recommender.recommender import Recommender

    datasets_root = datasets_root.resolve()
    profiles_dir  = profiles_dir.resolve()

    if not datasets_root.exists():
        logger.error("datasets_root does not exist: %s", datasets_root)
        sys.exit(1)

    dataset_dirs = sorted(
        d for d in datasets_root.iterdir()
        if d.is_dir() and d.name not in skip_datasets
    )
    if not dataset_dirs:
        logger.error("No dataset sub-directories found in %s", datasets_root)
        sys.exit(1)

    logger.info("Phase 1: profiling %d dataset(s) → %s", len(dataset_dirs), profiles_dir)
    profiles_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for i, dataset_dir in enumerate(dataset_dirs, 1):
        out_pkl = profiles_dir / f"{dataset_dir.name}.pkl"
        if out_pkl.exists():
            logger.info("[%d/%d] %s — SKIPPED (profile already exists)",
                        i, len(dataset_dirs), dataset_dir.name)
            continue

        logger.info("[%d/%d] %s — starting...", i, len(dataset_dirs), dataset_dir.name)
        t0 = time.monotonic()
        try:
            from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
            import pickle

            profiler = DeepProfiler()
            lang_profile = profiler.run_profile("building", parquet_dir=dataset_dir)

            if lang_profile.empty:
                logger.warning("[%d/%d] %s — empty profile, skipping.",
                               i, len(dataset_dirs), dataset_dir.name)
                continue

            with open(out_pkl, "wb") as fh:
                pickle.dump(lang_profile, fh, protocol=pickle.HIGHEST_PROTOCOL)

            elapsed = time.monotonic() - t0
            logger.info("[%d/%d] %s — done in %.1fs  (%d features, %d languages)",
                        i, len(dataset_dirs), dataset_dir.name,
                        elapsed, lang_profile.shape[0], lang_profile.shape[1])
            written += 1

        except Exception as exc:
            logger.error("[%d/%d] %s — FAILED: %s", i, len(dataset_dirs),
                         dataset_dir.name, exc, exc_info=True)
            # Continue to next dataset — do not abort the whole job.

    logger.info("Phase 1 complete: %d new profile(s) written.", written)
    return written


# ---------------------------------------------------------------------------
# Phase 2 — MKB assembly
# ---------------------------------------------------------------------------

def run_phase2(
    profiles_dir: Path,
    benchmark_dir: Path | None,
    mkb_output_path: Path,
    variance_threshold: float,
    max_pca_components: int,
    k: int,
    logger: logging.Logger,
) -> None:
    """Assemble the MKBStore from profiles + benchmarking results."""
    from lid_toolkit.recommender.recommender import Recommender

    profiles_dir = profiles_dir.resolve()
    mkb_output_path = mkb_output_path.resolve()

    if not profiles_dir.exists():
        logger.error("profiles_dir does not exist: %s", profiles_dir)
        sys.exit(1)

    pkl_count = len(list(profiles_dir.glob("*.pkl")))
    if pkl_count == 0:
        logger.error("No .pkl profile files found in %s — Phase 1 may have failed.",
                     profiles_dir)
        sys.exit(1)

    if benchmark_dir is None or not benchmark_dir.exists():
        logger.warning(
            "benchmark_dir not provided or does not exist (%s). "
            "Phase 2 will build an MKBStore WITHOUT performance data — "
            "the Recommender will only be able to compare linguistic profiles.",
            benchmark_dir,
        )
        # Pass an empty but valid path so build_from_filesystem can still run.
        benchmark_dir_arg = profiles_dir  # treated as empty benchmark dir
    else:
        benchmark_dir_arg = benchmark_dir.resolve()

    logger.info(
        "Phase 2: assembling MKBStore from %d profile(s) → %s",
        pkl_count, mkb_output_path,
    )
    t0 = time.monotonic()

    mkb_output_path.parent.mkdir(parents=True, exist_ok=True)
    Recommender.build_mkb(
        benchmark_dir=benchmark_dir_arg,
        profiles_dir=profiles_dir,
        output_path=mkb_output_path,
        variance_threshold=variance_threshold,
        max_pca_components=max_pca_components,
        k=k,
    )

    elapsed = time.monotonic() - t0
    logger.info("Phase 2 complete: MKBStore saved to %s  (%.1fs)", mkb_output_path, elapsed)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the lid_toolkit Meta-Knowledge Base on an HPC node."
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Path to config.yaml (default: config.yaml next to this script).",
    )
    parser.add_argument(
        "--skip-phase2", action="store_true",
        help="Run Phase 1 only (profiling). Useful for incremental runs.",
    )
    args = parser.parse_args()

    # ── Load config ──────────────────────────────────────────────────────────
    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    cfg = _load_yaml(config_path)
    base = config_path.parent

    paths_cfg     = cfg.get("paths", {})
    profiling_cfg = cfg.get("profiling", {})
    mkb_cfg       = cfg.get("mkb", {})
    log_cfg       = cfg.get("logging", {})

    # ── Resolve paths ────────────────────────────────────────────────────────
    datasets_root   = _resolve(paths_cfg.get("datasets_root"),   "LID_DATASETS_ROOT", base)
    profiles_dir    = _resolve(paths_cfg.get("profiles_dir"),    "LID_PROFILES_DIR",  base)
    benchmark_dir   = _resolve(paths_cfg.get("benchmark_dir"),   "LID_BENCHMARK_DIR", base)
    mkb_output_path = _resolve(paths_cfg.get("mkb_output_path"), "LID_MKB_OUTPUT",    base)

    # Apply defaults
    if profiles_dir is None:
        profiles_dir = base / "profiles"
    if mkb_output_path is None:
        mkb_output_path = base / "mkb.pkl"

    # ── Setup logging ────────────────────────────────────────────────────────
    log_level    = log_cfg.get("level", "INFO")
    log_filename = log_cfg.get("log_filename", "build_mkb.log")
    log_file     = profiles_dir.parent / log_filename

    _setup_logging(log_level, log_file)
    logger = logging.getLogger("hpc_build_mkb")

    # ── Log startup info ─────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("lid_toolkit MKB Build")
    logger.info("  config        : %s", config_path)
    logger.info("  datasets_root : %s", datasets_root)
    logger.info("  profiles_dir  : %s", profiles_dir)
    logger.info("  benchmark_dir : %s", benchmark_dir)
    logger.info("  mkb_output    : %s", mkb_output_path)
    logger.info("  skip_phase2   : %s", args.skip_phase2)
    logger.info("=" * 60)

    pbs_jobid = os.environ.get("PBS_JOBID", "local")
    logger.info("PBS_JOBID: %s", pbs_jobid)

    # ── Phase 1 ──────────────────────────────────────────────────────────────
    skip_datasets = profiling_cfg.get("skip_datasets", [])
    run_phase1(
        datasets_root=datasets_root,
        profiles_dir=profiles_dir,
        skip_datasets=skip_datasets,
        logger=logger,
    )

    # ── Phase 2 ──────────────────────────────────────────────────────────────
    if args.skip_phase2:
        logger.info("--skip-phase2 set. Exiting after Phase 1.")
        return

    run_phase2(
        profiles_dir=profiles_dir,
        benchmark_dir=benchmark_dir,
        mkb_output_path=mkb_output_path,
        variance_threshold=mkb_cfg.get("variance_threshold", 0.95),
        max_pca_components=mkb_cfg.get("max_pca_components", 20),
        k=mkb_cfg.get("k", 3),
        logger=logger,
    )

    logger.info("All phases complete.")


if __name__ == "__main__":
    main()
