import re

from tree_sitter import Language, Parser

from .gitparser import tokenize_code
from .lang import Lang


class SassData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(
            Language("./vendors/tree_sitter_so/language.so", "scss")
        )

    def test_file_filter(self, filename):
        return (
            filename.endswith(".sass") and not re.search(r"tests?/", filename) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith(".sass") and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
