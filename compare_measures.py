"""Utility for comparing two lists of profiler measures.

Reads two text files containing one measure per line and reports which
measures appear in the first file but not the second.

Usage::

    python compare_measures.py excess.txt expected.txt

The script will print the missing measures to stdout, one per line.
"""

import sys
from pathlib import Path


def read_measures(path: Path) -> set[str]:
    """Return a set of non-empty stripped lines from the given file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        lines = {line.strip() for line in f if line.strip()}
    return lines


# def main(args: list[str] | None = None) -> None:
#     if args is None:
#         args = sys.argv[1:]

#     if len(args) != 2:
#         print("Usage: python compare_measures.py <current_file> <expected_file>")
#         sys.exit(1)

#     current_path = Path(args[0])
#     expected_path = Path(args[1])

#     try:
#         current = read_measures(current_path)
#         expected = read_measures(expected_path)
#     except Exception as e:
#         print(f"Error reading files: {e}")
#         sys.exit(1)

#     missing = sorted(expected - current)
#     if not missing:
#         print("All measures in the expected file are present in the current file.")
#     else:
#         print("Measures present in expected file but missing in current file:")
#         for measure in missing:
#             print(measure)


def main(args: list[str] | None = None) -> None:
    # Use your specific paths if no args provided
    if not args and len(sys.argv) == 1:
        current_path = Path(r"C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\project_context\profiler_current_measures.txt")
        expected_path = Path(r"C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\project_context\profiler_expected_measures.txt")
    else:
        args = args or sys.argv[1:]
        if len(args) != 2:
            print("Usage: python compare_measures.py <current_file> <expected_file>")
            sys.exit(1)
        current_path, expected_path = Path(args[0]), Path(args[1])

    try:
        current = read_measures(current_path)
        expected = read_measures(expected_path)
        
        # Reports measures in FIRST file but not SECOND (per your docstring)
        excess = sorted(expected - current)
        
        if not excess:
            print("No excess measures found in current file.")
        else:
            print(f"Measures in {current_path.name} NOT in {expected_path.name}:")
            for m in excess: print(m)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
