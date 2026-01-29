"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: global_methods.py
Description: Common utility functions.
"""

import csv
import errno
import os
import shutil
from pathlib import Path
from typing import Iterable, List, Tuple, Set, Union

import numpy as np


# -------------------- FILE & FOLDER --------------------

def create_folder_if_not_there(path: Union[str, Path]) -> bool:
    """
    Create parent folder if it does not exist.
    Works for both file paths and directory paths.
    """
    path = Path(path)
    folder = path.parent if path.suffix else path

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return True
    return False


def check_if_file_exists(path: Union[str, Path]) -> bool:
    return Path(path).is_file()


def find_filenames(path_to_dir: Union[str, Path], suffix: str = ".csv") -> List[str]:
    path = Path(path_to_dir)
    return [str(p) for p in path.glob(f"*{suffix}")]


def copyanything(src: Union[str, Path], dst: Union[str, Path]) -> None:
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise


# -------------------- CSV --------------------

def write_list_of_list_to_csv(data: List[List], outfile: Union[str, Path]) -> None:
    create_folder_if_not_there(outfile)
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(data)


def write_list_to_csv_line(line: List, outfile: Union[str, Path]) -> None:
    create_folder_if_not_there(outfile)
    with open(outfile, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(line)


def read_file_to_list(
    curr_file: Union[str, Path],
    header: bool = False,
    strip_trail: bool = True,
) -> Union[List[List[str]], Tuple[List[str], List[List[str]]]]:

    with open(curr_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [
            [cell.strip() for cell in row] if strip_trail else row
            for row in reader
        ]

    if header:
        return rows[0], rows[1:]
    return rows


def read_file_to_set(curr_file: Union[str, Path], col: int = 0) -> Set[str]:
    with open(curr_file, newline="", encoding="utf-8") as f:
        return {row[col] for row in csv.reader(f) if row}


def get_row_len(curr_file: Union[str, Path]) -> Union[int, bool]:
    try:
        with open(curr_file, newline="", encoding="utf-8") as f:
            return sum(1 for _ in csv.reader(f))
    except FileNotFoundError:
        return False


# -------------------- MATH --------------------

def average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        raise ValueError("Cannot compute average of empty list")
    return sum(values) / len(values)


def std(values: Iterable[float]) -> float:
    return float(np.std(list(values)))


# -------------------- MAIN --------------------

if __name__ == "__main__":
    pass
