import re
from .lang import Lang

class CCData(Lang):

    def test_file_filter(self, filename):
        return (filename.endswith('.c') or filename.endswith('.cpp') or filename.endswith('.cu')) and (
            not re.match('tests?/', filename, re.I) is None or
            not re.match('/tests?', filename, re.I) is None
        )

    def src_file_filter(self, filename):
        return (filename.endswith('.c') or 
                filename.endswith('.cpp') or 
                filename.endswith('.cu')) and not self.test_file_filter(filename)

