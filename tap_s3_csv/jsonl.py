"""
JSON lines reading, mirroring singer_encodings' csv reader family.

Some S3 exports are one JSON object per line rather than CSV. A table opts in
with "format": "jsonl" in its table spec; CSV stays the default.
"""

from __future__ import annotations

import codecs
import json
from typing import Dict, Generator

from singer_encodings import compression


def get_row_iterators(
    iterable, options: Dict = None, infer_compression: bool = True
) -> Generator:
    """
    Accepts a file-like iterable and yields one row iterator per file member
    (a gzip file has one member, a zip archive may have several), the same
    contract as singer_encodings.csv.get_row_iterators.
    """
    options = options or {}
    if infer_compression:
        iterables = compression.infer(iterable, options.get("file_name"))
    else:
        iterables = [iterable]

    for item in iterables:
        yield _row_iterator(item, options)


def _row_iterator(file_stream, options: Dict) -> Generator:
    """
    Yields one dict per non-empty line. A line that is not valid JSON, or is
    JSON but not an object, raises with the line number so a malformed file
    fails loudly instead of loading partially.
    """
    encoding = options.get("encoding", "utf-8")
    for lineno, line in enumerate(
        codecs.iterdecode(file_stream, encoding), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError as err:
            raise ValueError(
                f"Line {lineno} is not valid JSON: {line[:120]!r}"
            ) from err
        if not isinstance(record, dict):
            raise ValueError(
                f"Line {lineno} is JSON but not an object: {line[:120]!r}"
            )
        yield record
