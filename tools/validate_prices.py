#!/usr/bin/env python3
"""Validate Portfolio Guard daily-price CSV without any network or DB writes."""
import argparse
import csv
import datetime as dt
import decimal
import io
import pathlib
import re
import sys

ISINS = {
    "DE0009770206", "FR0010524777", "IE00B3VWM098",
    "IE00B4KBBD01", "IE00BFMNPS42", "IE00BGQYRS42",
    "IE00BMX0B631", "IE00BWBXM617", "LU0321465469",
    "LU1799928095",
}
HEADER = ("isin", "date", "price", "source")


def validate(text, today=None):
    today = today or dt.date.today()
    text = text.removeprefix("\ufeff")
    nonempty = [line for line in text.splitlines() if line.strip()]
    if not nonempty:
        return [], ["Empty file"]
    separator = ";" if nonempty[0].count(";") > nonempty[0].count(",") else ","
    rows = csv.reader(io.StringIO("\n".join(nonempty)), delimiter=separator)
    header = tuple(part.strip().lower() for part in next(rows))
    if header != HEADER:
        return [], ["Expected exact columns: " + ",".join(HEADER)]
    errors, result, last_dates = [], [], {}
    for number, row in enumerate(rows, start=2):
        if len(row) != 4:
            errors.append(f"Line {number}: expected four columns")
            continue
        isin, day, price, source = (v.strip() for v in row)
        if isin not in ISINS:
            errors.append(f"Line {number}: unknown ISIN {isin}")
            continue
        try:
            parsed_date = dt.date.fromisoformat(day)
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) or parsed_date > today:
                raise ValueError()
        except ValueError:
            errors.append(f"Line {number}: invalid or future ISO date")
            continue
        try:
            if not re.fullmatch(r"\d+(\.\d+)?", price):
                raise ValueError()
            value = decimal.Decimal(price)
            if not decimal.Decimal("0") < value <= decimal.Decimal("1000000000"):
                raise ValueError()
            if abs(value.as_tuple().exponent) > 6:
                raise ValueError()
        except (ValueError, decimal.InvalidOperation):
            errors.append(f"Line {number}: invalid price (dot decimal, max 6 places)")
            continue
        if not 3 <= len(source) <= 200:
            errors.append(f"Line {number}: source must contain 3-200 chars")
            continue
        if isin in last_dates and parsed_date <= last_dates[isin]:
            errors.append(f"Line {number}: dates for each ISIN must increase strictly")
            continue
        last_dates[isin] = parsed_date
        result.append((isin, day, price, source))
    return result, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=pathlib.Path)
    args = parser.parse_args()
    try:
        rows, errors = validate(args.csv_file.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError) as exc:
        print(f"Could not read file: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} issue(s); no data uploaded")
        return 1
    print(f"PASS: {len(rows)} valid observations; no data uploaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
