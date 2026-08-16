"""Core JSONL parsing and transformation functions."""

from dataclasses import dataclass
import json
from typing import Any, Dict, Iterable, Iterator, Sequence, TextIO


class JsonlError(ValueError):
    """Raised when an input line is not valid JSON."""

    def __init__(self, line_number: int, message: str) -> None:
        self.line_number = line_number
        self.message = message
        super().__init__(f"line {line_number}: {message}")


@dataclass(frozen=True)
class JsonlRecord:
    """A parsed JSON value together with its source line number."""

    line_number: int
    value: Any


def iter_jsonl(source: TextIO, *, skip_blank: bool = False) -> Iterator[JsonlRecord]:
    """Yield parsed JSONL records from a text stream.

    The function processes one line at a time and therefore supports inputs that
    are larger than available memory.
    """

    for line_number, raw_line in enumerate(source, start=1):
        text = raw_line.strip()
        if not text:
            if skip_blank:
                continue
            raise JsonlError(line_number, "blank line")

        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise JsonlError(line_number, exc.msg) from exc

        yield JsonlRecord(line_number=line_number, value=value)


def select_fields(value: Any, fields: Sequence[str], *, include_missing: bool = False) -> Dict[str, Any]:
    """Return selected fields from a JSON object.

    Non-object values are rejected because field selection has no unambiguous
    meaning for arrays, strings, numbers, booleans, or null.
    """

    if not isinstance(value, dict):
        raise TypeError("field selection requires a JSON object")

    if include_missing:
        return {field: value.get(field) for field in fields}
    return {field: value[field] for field in fields if field in value}


def encode_records(records: Iterable[Any]) -> Iterator[str]:
    """Encode values as compact, Unicode-preserving JSON lines."""

    for record in records:
        yield json.dumps(record, ensure_ascii=False, separators=(",", ":"))


def project_records(
    records: Iterable[JsonlRecord],
    fields: Sequence[str],
    *,
    include_missing: bool = False,
) -> Iterator[JsonlRecord]:
    """Project object records onto ``fields`` while preserving line numbers."""

    for record in records:
        yield JsonlRecord(
            line_number=record.line_number,
            value=select_fields(
                record.value,
                fields,
                include_missing=include_missing,
            ),
        )
