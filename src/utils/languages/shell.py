import re

from tree_sitter import Language, Parser

from .lang import Lang


class ShellData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(
            Language("./vendors/tree_sitter_so/language.so", "java")
        )

    def test_file_filter(self, filename):
        return filename.endswith(".sh") and not re.search(r"tests?/", filename) is None

    def src_file_filter(self, filename):
        return filename.endswith(".sh") and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines
