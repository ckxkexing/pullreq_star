import re
from .lang import Lang
from tree_sitter import Language, Parser
from .gitparser import tokenize_code

class RubyData(Lang):
    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language('./vendors/tree_sitter_so/language.so', 'ruby'))

    def test_file_filter(self, filename):
        return filename.endswith('.rb') and (
            ('test/' in filename or
            'tests/' in filename or
            'spec/' in filename) and
            'lib/' not in filename)


    def src_file_filter(self, filename):
        return filename.endswith('.rb') and not self.test_file_filter(filename)

    # rails/rails : RSpec
    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)
