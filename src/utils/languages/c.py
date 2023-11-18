import re

from tree_sitter import Language, Parser

from .gitparser import tokenize_code
from .lang import Lang


class CData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language("./vendors/tree_sitter_so/language.so", "c"))

    def test_file_filter(self, filename):
        return filename.endswith(".c") and (
            not re.search(r"tests?/", filename, re.I) is None
            or not re.search(r"/tests?", filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith(".c") and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
