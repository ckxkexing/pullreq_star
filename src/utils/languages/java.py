import re
from .lang import Lang

class JavaData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.java') and (
            not re.match(r'tests?/', filename) is None or
            not re.match(r'[tT]est.java', filename) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.java') and not self.test_file_filter(filename)

