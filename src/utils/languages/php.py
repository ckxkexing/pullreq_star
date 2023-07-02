import re
from .lang import Lang

class PhpData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.php') and not re.match('tests?/', filename) is None


    def src_file_filter(self, filename):
        return filename.endswith('.php') and not self.test_file_filter(filename)

