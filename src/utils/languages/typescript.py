import re

from tree_sitter import Language, Parser

from .gitparser import tokenize_code
from .lang import Lang


class TypescriptData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(
            Language("./vendors/tree_sitter_so/language.so", "typescript")
        )

    def test_file_filter(self, filename):
        return (filename.endswith(".ts") or filename.endswith(".js")) and (
            "spec/" in filename
            or "test/" in filename
            or "tests/" in filename
            or "testing/" in filename
            or "__tests__" in filename
            or not re.search(r".+spec\.ts", filename, re.I) is None
            or not re.search(r".+test\.ts", filename, re.I) is None
            or not re.search(r".+spec\.js", filename, re.I) is None
            or not re.search(r".+test\.js", filename, re.I) is None
            or not re.search(r"test-.+", filename, re.I) is None
            or not re.search(r"test_.+", filename, re.I) is None
            or not re.search(r".+-test", filename, re.I) is None
            or not re.search(r".+_test", filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith(".ts") and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
