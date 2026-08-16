"""Command-line interface for jsonl-stream-utils."""

import argparse
from contextlib import contextmanager
import sys
from typing import Iterator, Optional, Sequence, TextIO

from .core import JsonlError, encode_records, iter_jsonl, select_fields


@contextmanager
def open_input(path: str) -> Iterator[TextIO]:
    if path == "-":
        yield sys.stdin
        return

    with open(path, "r", encoding="utf-8") as stream:
        yield stream


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jsonl-stream-utils",
        description="Validate and transform JSON Lines streams.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a JSONL stream")
    validate.add_argument("path", help="input path, or - for standard input")
    validate.add_argument("--skip-blank", action="store_true", help="ignore blank lines")

    select = subparsers.add_parser("select", help="select fields from JSON objects")
    select.add_argument("path", help="input path, or - for standard input")
    select.add_argument("--fields", required=True, help="comma-separated field names")
    select.add_argument("--include-missing", action="store_true", help="emit missing fields as null")
    select.add_argument("--skip-blank", action="store_true", help="ignore blank lines")
    return parser


def run_validate(path: str, *, skip_blank: bool) -> int:
    with open_input(path) as source:
        count = sum(1 for _ in iter_jsonl(source, skip_blank=skip_blank))
    print(f"valid: {count} record(s)")
    return 0


def run_select(
    path: str,
    *,
    fields: Sequence[str],
    include_missing: bool,
    skip_blank: bool,
) -> int:
    with open_input(path) as source:
        selected = (
            select_fields(record.value, fields, include_missing=include_missing)
            for record in iter_jsonl(source, skip_blank=skip_blank)
        )
        for encoded in encode_records(selected):
            print(encoded)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            return run_validate(args.path, skip_blank=args.skip_blank)

        fields = [field.strip() for field in args.fields.split(",") if field.strip()]
        if not fields:
            raise ValueError("--fields must contain at least one field name")
        return run_select(
            args.path,
            fields=fields,
            include_missing=args.include_missing,
            skip_blank=args.skip_blank,
        )
    except (JsonlError, OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
