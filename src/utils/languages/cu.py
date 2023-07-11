import re
from .lang import Lang
from tree_sitter import Language, Parser
from .gitparser import tokenize_code

class CUData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language('./vendors/tree_sitter_so/language.so', 'cuda'))

    def test_file_filter(self, filename):
        return (filename.endswith('.cu') ) and (
            not re.search(r'tests?/', filename, re.I) is None or
            not re.search(r'/tests?', filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.cu') and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
