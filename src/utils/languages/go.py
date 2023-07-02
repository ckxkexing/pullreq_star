from .lang import Lang
import re
class GoData:
    def test_file_filter(self, filename):
        return filename.endswith('.go') and (
            filename.endswith('_test.go') or
            not re.match('test_.+', filename, re.I) is None or
            not re.match('.+_test', filename, re.I) is None or
            not re.match('tests?/', filename, re.I) is None
        )


    def src_file_filter(self, filename):
        return filename.endswith('.go') and not self.test_file_filter(filename)

