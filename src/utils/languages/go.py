import re

from tree_sitter import Language, Parser

from .gitparser import tokenize_code
from .lang import strip_c_style_comments


class GoData:
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language("./vendors/tree_sitter_so/language.so", "go"))

    def test_file_filter(self, filename):
        return filename.endswith(".go") and (
            filename.endswith(r"_test.go")
            or not re.search(r"test_.+", filename, re.I) is None
            or not re.search(r".+_test", filename, re.I) is None
            or not re.search(r"tests?/", filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith(".go") and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return strip_c_style_comments(lines)

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
