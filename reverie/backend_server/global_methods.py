"""
Author: Joon Sung Park (joonspk@stanford.edu)

Optimized utility helpers for filesystem, CSV, and statistics operations.
"""

from __future__ import annotations

import csv
import errno
import shutil
from pathlib import Path
from typing import Iterable, Any

import numpy as np


# =========================================================
# Filesystem Helpers
# =========================================================

def create_folder_if_not_there(path: str | Path) -> bool:
    """
    Create parent folder(s) if they do not exist.

    Args:
        path: File or directory path.

    Returns:
        True if a folder was created, False otherwise.
    """
    path = Path(path)

    # If path has suffix → assume file path
    folder = path.parent if path.suffix else path

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return True

    return False


def check_if_file_exists(path: str | Path) -> bool:
    """
    Check whether a file exists.
    """
    return Path(path).exists()


def find_filenames(path_to_dir: str | Path, suffix: str = ".csv") -> list[str]:
    """
    Find all files in a directory matching suffix.

    Args:
        path_to_dir: Directory path
        suffix: File suffix filter

    Returns:
        List of matching file paths.
    """
    path = Path(path_to_dir)

    return [
        str(file)
        for file in path.iterdir()
        if file.is_file() and file.name.endswith(suffix)
    ]


def copyanything(src: str | Path, dst: str | Path) -> None:
    """
    Copy files or directories recursively.
    """
    src = Path(src)
    dst = Path(dst)

    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise


# =========================================================
# CSV Helpers
# =========================================================

def write_list_of_list_to_csv(
    rows: Iterable[Iterable[Any]],
    outfile: str | Path,
) -> None:
    """
    Write multiple rows to CSV.
    """
    create_folder_if_not_there(outfile)

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def write_list_to_csv_line(
    row: Iterable[Any],
    outfile: str | Path,
) -> None:
    """
    Append a single row to CSV.
    """
    create_folder_if_not_there(outfile)

    with open(outfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def read_file_to_list(
    curr_file: str | Path,
    header: bool = False,
    strip_trail: bool = True,
):
    """
    Read CSV into list.

    Args:
        curr_file: CSV path
        header: Return header separately
        strip_trail: Strip whitespace

    Returns:
        List of rows OR tuple(header, rows)
    """
    with open(curr_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        rows = [
            [cell.strip() for cell in row] if strip_trail else row
            for row in reader
        ]

    if header:
        return rows[0], rows[1:]

    return rows


def read_file_to_set(
    curr_file: str | Path,
    col: int = 0,
) -> set[str]:
    """
    Read a CSV column into a set.
    """
    with open(curr_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        return {
            row[col]
            for row in reader
            if len(row) > col
        }


def get_row_len(curr_file: str | Path) -> int | bool:
    """
    Count unique rows based on first column.

    Returns:
        Number of unique rows OR False if file does not exist.
    """
    try:
        with open(curr_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            return len({
                row[0]
                for row in reader
                if row
            })

    except FileNotFoundError:
        return False


# =========================================================
# Statistics Helpers
# =========================================================

def average(values: Iterable[float]) -> float:
    """
    Calculate average.
    """
    values = list(values)

    if not values:
        raise ValueError("values cannot be empty")

    return sum(values) / len(values)


def std(values: Iterable[float]) -> float:
    """
    Calculate standard deviation.
    """
    values = list(values)

    if not values:
        raise ValueError("values cannot be empty")

    return float(np.std(values))


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    pass
