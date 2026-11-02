import tempfile
import unittest
from pathlib import Path

from compatibility import audit, blank_noncode


class AuditTests(unittest.TestCase):
    def test_lua_comments_and_strings_are_ignored(self):
        source = (
            "-- loadstring(game:HttpGet('example'))\n"
            'local s = "readfile gethui"\n'
            '--[=[ getgenv writefile ]=]\n'
            'local long_text = [==[ getcustomasset ]==]\n'
            'if type(getgenv) == "function" then\n'
            '    local source = game:HttpGet("https://example.com")\n'
            '    loadstring(source)()\n'
            'end\n'
        )
        clean = blank_noncode(source)
        self.assertEqual(clean.count("\n"), source.count("\n"))
        self.assertNotIn("gethui", clean)
        self.assertNotIn("readfile", clean)
        self.assertNotIn("getcustomasset", clean)
        self.assertIn("getgenv", clean)
        self.assertIn("game:HttpGet", clean)
        self.assertIn("loadstring", clean)

    def test_request_function_is_not_http_executor(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Monarca.lua"
            path.write_text(
                'local function request(value) return value end\n'
                'request(true)\n'
                'if type(readfile) == "function" then readfile("a") end\n'
                'if type(getgenv) == "function" then getgenv() end\n'
                '-- loadstring(fake)\n',
                encoding="utf-8",
            )
            result = audit(Path(directory))
            groups = result["api_groups"]
            self.assertEqual(groups["executor_http"]["matches"], 0)
            self.assertEqual(groups["dynamic_code"]["matches"], 0)
            self.assertEqual(groups["executor_filesystem"]["matches"], 2)
            self.assertEqual(groups["executor_environment"]["matches"], 2)

    def test_missing_files_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                audit(Path(directory) / "missing")


if __name__ == "__main__":
    unittest.main()
