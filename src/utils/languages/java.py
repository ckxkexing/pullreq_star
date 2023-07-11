import re
from .lang import Lang
from tree_sitter import Language, Parser
from .gitparser import tokenize_code

class JavaData(Lang):

    def __init__(self):
        self.PARSER = Parser()
        self.PARSER.set_language(Language('./vendors/tree_sitter_so/language.so', 'java'))

    def test_file_filter(self, filename):
        return filename.endswith('.java') and (
            not re.search(r'tests?/', filename) is None or
            not re.search(r'[tT]ests?\.java', filename) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.java') and not self.test_file_filter(filename)

    def strip_comments(self, lines):
        return lines

    def tokenize(self, lines):
        return tokenize_code(self.PARSER, lines)

def test1():
    filename = 'modules/test/integration/src/test/java/org/elasticsearch/test/integration/search/scan/SearchScanTests.java'
    linguist = JavaData()
    assert linguist.test_file_filter(filename) == True