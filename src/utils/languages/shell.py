import re
from .lang import Lang

class ShellData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.sh') and not re.match('tests?/', filename) is None


    def src_file_filter(self, filename):
        return filename.endswith('.sh') and not self.test_file_filter(filename)

