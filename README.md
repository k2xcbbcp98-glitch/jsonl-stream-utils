# jsonl-stream-utils

A small, dependency-free Python toolkit for validating and transforming JSON Lines (JSONL) streams.

## Features

- Validate JSONL from files or standard input
- Report malformed lines with line numbers
- Skip blank lines when requested
- Keep only selected object fields
- Project fields across a parsed stream while preserving source line numbers
- Validate basic OHLCV research records without connecting to a broker
- Normalize validated OHLCV records to stable field types
- Stream records without loading the whole input into memory
- Run on Python 3.9 or later with no third-party dependencies

## Installation

Clone the repository and run the module directly:

```bash
python -m jsonl_stream_utils --help
```

For an editable local installation:

```bash
python -m pip install -e .
```

## Usage

Validate a file:

```bash
python -m jsonl_stream_utils validate examples/sample.jsonl
```

Validate standard input:

```bash
type examples\sample.jsonl | python -m jsonl_stream_utils validate -
```

Select fields from JSON objects:

```bash
python -m jsonl_stream_utils select examples/sample.jsonl --fields id,name
```

Output:

```json
{"id":1,"name":"alpha"}
{"id":2,"name":"beta"}
```

## Development

Run the standard-library test suite:

```bash
python -m unittest discover -s tests -v
```

## License

MIT
