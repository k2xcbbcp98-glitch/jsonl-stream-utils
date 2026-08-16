import io
import unittest

from jsonl_stream_utils import JsonlError, iter_jsonl, project_records, select_fields


class IterJsonlTests(unittest.TestCase):
    def test_parses_objects_and_scalars(self):
        records = list(iter_jsonl(io.StringIO('{"id": 1}\n[1, 2]\ntrue\n')))
        self.assertEqual([record.line_number for record in records], [1, 2, 3])
        self.assertEqual([record.value for record in records], [{"id": 1}, [1, 2], True])

    def test_reports_invalid_line_number(self):
        with self.assertRaises(JsonlError) as caught:
            list(iter_jsonl(io.StringIO('{"ok": true}\nnot-json\n')))
        self.assertEqual(caught.exception.line_number, 2)

    def test_blank_lines_can_be_skipped(self):
        records = list(iter_jsonl(io.StringIO('\n{"id": 1}\n'), skip_blank=True))
        self.assertEqual(records[0].line_number, 2)


class SelectFieldsTests(unittest.TestCase):
    def test_selects_existing_fields(self):
        self.assertEqual(select_fields({"id": 1, "name": "a"}, ["name"]), {"name": "a"})

    def test_can_include_missing_fields(self):
        result = select_fields({"id": 1}, ["id", "name"], include_missing=True)
        self.assertEqual(result, {"id": 1, "name": None})

    def test_rejects_non_objects(self):
        with self.assertRaises(TypeError):
            select_fields([1, 2], ["id"])


class ProjectRecordsTests(unittest.TestCase):
    def test_projects_stream_and_preserves_line_numbers(self):
        source = io.StringIO('{"id": 1, "name": "alpha"}\n\n{"id": 2}\n')
        records = iter_jsonl(source, skip_blank=True)

        projected = list(project_records(records, ["name"], include_missing=True))

        self.assertEqual([record.line_number for record in projected], [1, 3])
        self.assertEqual([record.value for record in projected], [{"name": "alpha"}, {"name": None}])


if __name__ == "__main__":
    unittest.main()
