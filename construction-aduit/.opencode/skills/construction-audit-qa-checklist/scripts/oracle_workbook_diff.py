#!/usr/bin/env python3
"""
oracle_workbook_diff.py - deterministic workbook diff helpers for QA/oracle checks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import xlrd


def _col_letter(index: int) -> str:
    result = ""
    n = index + 1
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _normalize(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 12)
    return value


def diff_sheet_cells(
    correct_workbook_path: Path,
    wrong_workbook_path: Path,
    sheet_name: str,
) -> list[dict[str, Any]]:
    correct = xlrd.open_workbook(file_contents=correct_workbook_path.read_bytes(), formatting_info=True)
    wrong = xlrd.open_workbook(file_contents=wrong_workbook_path.read_bytes(), formatting_info=True)

    correct_sheet = correct.sheet_by_name(sheet_name)
    wrong_sheet = wrong.sheet_by_name(sheet_name)

    diffs: list[dict[str, Any]] = []
    for row_index in range(max(correct_sheet.nrows, wrong_sheet.nrows)):
        for col_index in range(max(correct_sheet.ncols, wrong_sheet.ncols)):
            correct_value = correct_sheet.cell_value(row_index, col_index) if row_index < correct_sheet.nrows and col_index < correct_sheet.ncols else ""
            wrong_value = wrong_sheet.cell_value(row_index, col_index) if row_index < wrong_sheet.nrows and col_index < wrong_sheet.ncols else ""
            normalized_correct = _normalize(correct_value)
            normalized_wrong = _normalize(wrong_value)
            if normalized_correct == normalized_wrong:
                continue
            diffs.append(
                {
                    "cell_ref": f"{_col_letter(col_index)}{row_index + 1}",
                    "correct_value": normalized_correct,
                    "wrong_value": normalized_wrong,
                }
            )
    return diffs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff one sheet between the correct and wrong workbooks.")
    parser.add_argument("--correct-workbook", required=True, help="Path to the correct/oracle workbook")
    parser.add_argument("--wrong-workbook", required=True, help="Path to the workbook under review")
    parser.add_argument("--sheet-name", required=True, help="Target sheet name")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    diffs = diff_sheet_cells(
        Path(args.correct_workbook),
        Path(args.wrong_workbook),
        args.sheet_name,
    )
    print(json.dumps(diffs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
