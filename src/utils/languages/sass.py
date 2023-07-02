import re
from .lang import Lang

class SassData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.sass') and not re.match('tests?/', filename) is None


    def src_file_filter(self, filename):
        return filename.endswith('.sass') and not self.test_file_filter(filename)

