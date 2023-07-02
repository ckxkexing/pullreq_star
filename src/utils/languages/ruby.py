import re
from .lang import Lang

class RubyData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.rb') and (
            ('test/' in filename or
            'tests/' in filename or
            'spec/' in filename) and
            'lib/' not in filename)


    def src_file_filter(self, filename):
        return filename.endswith('.rb') and not self.test_file_filter(filename)
