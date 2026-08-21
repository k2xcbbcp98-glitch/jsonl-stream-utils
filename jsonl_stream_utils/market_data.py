"""Small, dependency-free helpers for validating bar data in research files."""

from collections.abc import Iterable, Mapping
from typing import Any


REQUIRED_BAR_FIELDS = ("symbol", "timestamp", "open", "high", "low", "close", "volume")


def validate_bar(row: Mapping[str, Any]) -> list[str]:
    """Return validation errors for one OHLCV research record.

    This validates file shape only. It does not assess a security or produce
    trading advice.
    """

    errors: list[str] = []
    for field in REQUIRED_BAR_FIELDS:
        if field not in row:
            errors.append(f"missing field: {field}")

    if errors:
        return errors

    numeric_fields = ("open", "high", "low", "close", "volume")
    for field in numeric_fields:
        value = row[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{field} must be numeric")
        elif value < 0 or (field != "volume" and value == 0):
            errors.append(f"{field} must be non-negative and non-zero for prices")

    if all(isinstance(row[field], (int, float)) and not isinstance(row[field], bool) for field in ("open", "high", "low", "close")):
        if row["high"] < max(row["open"], row["close"]) or row["low"] > min(row["open"], row["close"]):
            errors.append("high/low range does not contain open and close")
        if row["low"] > row["high"]:
            errors.append("low must not exceed high")

    return errors


def valid_bars(rows: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Keep only records that pass :func:`validate_bar`."""

    return [row for row in rows if not validate_bar(row)]


def normalize_bar(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return a validated bar with canonical field types.

    Symbols and timestamps are represented as strings and numeric OHLCV values
    are represented as floats. The function is intentionally limited to shape
    normalization; it does not fill missing market data or infer prices.
    """

    errors = validate_bar(row)
    if errors:
        raise ValueError("; ".join(errors))

    return {
        "symbol": str(row["symbol"]),
        "timestamp": str(row["timestamp"]),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": float(row["volume"]),
    }
