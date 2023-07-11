import re
from .lang import Lang
from tree_sitter import Language, Parser
from .gitparser import tokenize_code

class DartData(Lang):

    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language('./vendors/tree_sitter_so/language.so', 'dart'))

    def test_file_filter(self, filename):
        return filename.endswith('.dart') and (
            not re.search(r'/test_.*\/', filename) is None or
            not re.search(r'_[tT]est\.dart', filename) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.dart') and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
