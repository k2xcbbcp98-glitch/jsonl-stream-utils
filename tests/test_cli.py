import contextlib
import io
import os
import tempfile
import unittest

from jsonl_stream_utils.cli import main


class CliTests(unittest.TestCase):
    def make_input(self, content):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        with handle:
            handle.write(content)
        return handle.name

    def test_validate_success(self):
        path = self.make_input('{"id":1}\n{"id":2}\n')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["validate", path])
        self.assertEqual(code, 0)
        self.assertEqual(output.getvalue(), "valid: 2 record(s)\n")

    def test_select_fields(self):
        path = self.make_input('{"id":1,"name":"alpha","extra":true}\n')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["select", path, "--fields", "id,name"])
        self.assertEqual(code, 0)
        self.assertEqual(output.getvalue(), '{"id":1,"name":"alpha"}\n')

    def test_invalid_json_returns_error_code(self):
        path = self.make_input("not-json\n")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(["validate", path])
        self.assertEqual(code, 2)
        self.assertIn("line 1", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
