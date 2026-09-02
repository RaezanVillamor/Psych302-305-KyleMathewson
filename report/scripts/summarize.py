#!/usr/bin/env python3
"""Read a Week 2 RT or Week 3 inventory CSV and write generated report snippets.

Standard library only. Run from the report/ folder:

    python scripts/summarize.py --csv ../data/yourfile.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

RT_MIN = 150.0
RT_MAX = 2500.0
INV_MIN = 1.0
INV_MAX = 5.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate report numbers from a CSV.")
    parser.add_argument("--csv", required=True, type=Path, help="Path to a reaction-time or inventory CSV")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Directory for generated snippets")
    parser.add_argument("--report", type=Path, default=Path("REPORT.md"), help="Markdown file with generated markers")
    return parser.parse_args()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        lines = [line for line in handle if line.strip() and not line.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    if reader.fieldnames is None:
        raise SystemExit(f"No header row in {path}")
    headers = [name.strip() for name in reader.fieldnames]
    rows = []
    for raw in reader:
        rows.append({key.strip(): (raw.get(key) or "").strip() for key in reader.fieldnames})
    return headers, rows


def detect_kind(headers: list[str]) -> str:
    names = {name.lower() for name in headers}
    if "rt" in names:
        return "rt"
    if "scored" in names:
        return "inventory"
    return "numeric"


def first_numeric_column(headers: list[str], rows: list[dict[str, str]]) -> str:
    for name in headers:
        for row in rows:
            try:
                float(row[name])
                return name
            except ValueError:
                continue
    raise SystemExit("No numeric column found.")


def usable_values(kind: str, headers: list[str], rows: list[dict[str, str]]) -> tuple[str, float, float, list[float]]:
    if kind == "rt":
        column = next(name for name in headers if name.lower() == "rt")
        low, high = RT_MIN, RT_MAX
    elif kind == "inventory":
        column = next(name for name in headers if name.lower() == "scored")
        low, high = INV_MIN, INV_MAX
    else:
        column = first_numeric_column(headers, rows)
        low, high = float("-inf"), float("inf")
    values: list[float] = []
    for row in rows:
        try:
            value = float(row[column])
        except ValueError:
            continue
        if low <= value <= high:
            values.append(value)
    return column, low, high, values


def format_mean(value: float, kind: str) -> str:
    if kind == "rt":
        return f"{value:.0f} ms"
    return f"{value:.2f}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def splice_report(path: Path, body: str) -> None:
    if not path.exists():
        return
    start = "<!-- begin generated -->"
    end = "<!-- end generated -->"
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        return
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    path.write_text(f"{before}{start}\n{body.rstrip()}\n{end}{after}", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")
    headers, rows = read_rows(args.csv)
    kind = detect_kind(headers)
    column, low, high, values = usable_values(kind, headers, rows)
    n = len(values)
    if n == 0:
        raise SystemExit("No usable values after exclusion. Check the file and the range.")
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else None
    excluded = len(rows) - n
    mean_text = format_mean(mean, kind)
    sd_text = "—" if sd is None else format_mean(sd, kind)
    if kind == "rt":
        label = "reaction time"
        range_text = f"times under {low:.0f} ms or over {high:.0f} ms were excluded"
    elif kind == "inventory":
        label = "inventory item scores"
        range_text = f"scores outside {low:.0f}–{high:.0f} were excluded"
    else:
        label = f"column `{column}`"
        range_text = "no default exclusion range"
    md = (
        f"File `{args.csv.name}`: {n} usable values of {label} "
        f"(column `{column}`). Mean = {mean_text}"
        + (f", SD = {sd_text}" if sd is not None else "")
        + f". {excluded} row(s) excluded; {range_text}.\n"
    )
    tex_mean = f"{mean:.0f}" if kind == "rt" else f"{mean:.2f}"
    tex_sd = "---" if sd is None else (f"{sd:.0f}" if kind == "rt" else f"{sd:.2f}")
    unit = "~ms" if kind == "rt" else ""
    tex = (
        f"File \\texttt{{{args.csv.name}}}: $n={n}$ usable values. "
        f"Mean = ${tex_mean}${unit}"
        + (f", $SD={tex_sd}${unit}" if sd is not None else "")
        + f". {excluded} row(s) excluded.\n"
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_text(args.out / "numbers.md", md)
    write_text(args.out / "numbers.tex", tex)
    splice_report(args.report, md)
    print(md.rstrip())
    print(f"wrote {args.out / 'numbers.md'}")
    print(f"wrote {args.out / 'numbers.tex'}")
    if args.report.exists():
        print(f"updated {args.report} between generated markers")


if __name__ == "__main__":
    main()
