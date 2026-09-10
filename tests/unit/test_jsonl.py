"""JSON lines reader, and the per-table format switch that selects it."""
import gzip
import io
import unittest

from tap_s3_csv import jsonl, s3


def _gz(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(data)
    buf.seek(0)
    return buf


class _Handle:
    def __init__(self, data):
        self._raw_stream = io.BytesIO(data)


class TestJsonlReader(unittest.TestCase):
    def test_reads_gzipped_json_lines(self):
        payload = b'{"id": 1, "name": "ann"}\n{"id": 2, "name": "bob"}\n'
        readers = jsonl.get_row_iterators(_gz(payload), options={"file_name": "f.jsonl.gz"})
        rows = [r for it in readers for r in it]
        self.assertEqual([r["name"] for r in rows], ["ann", "bob"])

    def test_reads_plain_json_lines_and_skips_blank_lines(self):
        payload = b'{"id": 1}\n\n{"id": 2}\n'
        readers = jsonl.get_row_iterators(io.BytesIO(payload), options={"file_name": "f.jsonl"}, infer_compression=False)
        self.assertEqual([r["id"] for it in readers for r in it], [1, 2])

    def test_invalid_json_line_raises_with_line_number(self):
        payload = b'{"id": 1}\nnot json\n'
        readers = jsonl.get_row_iterators(io.BytesIO(payload), options={}, infer_compression=False)
        with self.assertRaises(ValueError) as ctx:
            list(next(readers))
        self.assertIn("Line 2", str(ctx.exception))

    def test_non_object_line_raises(self):
        readers = jsonl.get_row_iterators(io.BytesIO(b"[1, 2]\n"), options={}, infer_compression=False)
        with self.assertRaises(ValueError):
            list(next(readers))


class TestFormatSwitch(unittest.TestCase):
    def test_jsonl_format_uses_json_reader(self):
        handle = _Handle(_gz(b'{"id": 7}\n').getvalue())
        rows = [r for it in s3.row_iterators_for_table(handle, {"table_name": "t", "format": "jsonl"}, "f.jsonl.gz") for r in it]
        self.assertEqual(rows, [{"id": 7}])

    def test_default_is_csv(self):
        handle = _Handle(b"id,name\n1,ann\n")
        rows = [r for it in s3.row_iterators_for_table(handle, {"table_name": "t", "delimiter": ","}, "f.csv") for r in it]
        self.assertEqual(rows[0]["name"], "ann")


if __name__ == "__main__":
    unittest.main()
