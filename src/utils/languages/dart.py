import re
from .lang import Lang

class DartData(Lang):

    def test_file_filter(self, filename):
        return filename.endswith('.dart') and (
            not re.match(r'/test_.*\/', filename) is None or
            not re.match(r'_[tT]est.dart', filename) is None
        )

    def src_file_filter(self, filename):
        return filename.endswith('.dart') and not self.test_file_filter(filename)

