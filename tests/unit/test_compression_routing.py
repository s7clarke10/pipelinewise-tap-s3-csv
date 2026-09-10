"""
Reads go through singer_encodings' compression layer, so a gzipped file
produces the same rows as the plain file, and a zip yields every member.
"""
import gzip
import io
import unittest
import zipfile

from tap_s3_csv import s3

CSV = b"id,name\n1,ann\n2,bob\n"
SPEC = {"table_name": "people", "key_properties": ["id"], "delimiter": ","}


class _Handle:  # stands in for the botocore StreamingBody
    def __init__(self, data):
        self._raw_stream = io.BytesIO(data)


def _rows(handle, name):
    return [row for it in s3.row_iterators_for_table(handle, SPEC, name) for row in it]


class TestCompressionRouting(unittest.TestCase):
    def test_plain_csv_is_unchanged(self):
        rows = _rows(_Handle(CSV), "people.csv")
        self.assertEqual([r["name"] for r in rows], ["ann", "bob"])

    def test_gzipped_csv_yields_the_same_rows(self):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(CSV)
        rows = _rows(_Handle(buf.getvalue()), "people.csv.gz")
        self.assertEqual([r["name"] for r in rows], ["ann", "bob"])

    def test_zip_yields_every_member(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("a.csv", CSV)
            zf.writestr("b.csv", b"id,name\n3,cid\n")
        rows = _rows(_Handle(buf.getvalue()), "people.zip")
        self.assertEqual([r["name"] for r in rows], ["ann", "bob", "cid"])


if __name__ == "__main__":
    unittest.main()
