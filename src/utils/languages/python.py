import re
from .lang import Lang

class PythonData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.py') and (
            not re.match('test_.+', filename, re.I) is None or
            not re.match('.+_test', filename, re.I) is None or
            not re.match('test.py', filename, re.I) is None or
            not re.match('tests?/', filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.py') and not self.test_file_filter(filename)

