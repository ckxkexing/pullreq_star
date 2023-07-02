import re
from .lang import Lang

class TypescriptData(Lang):
    def test_file_filter(self, filename):
        return (filename.endswith('.ts') or filename.endswith('.js')) and (
            'spec/' in filename or
            'test/' in filename or
            'tests/' in filename or
            'testing/' in filename or
            '__tests__' in filename or
            not re.match('.+spec\.ts', filename, re.I) is None or
            not re.match('.+test\.ts', filename, re.I) is None or
            not re.match('.+spec\.js', filename, re.I) is None or
            not re.match('.+test\.js', filename, re.I) is None or
            not re.match('test-.+', filename, re.I) is None or
            not re.match('test_.+', filename, re.I) is None or
            not re.match('.+-test', filename, re.I) is None or
            not re.match('.+_test', filename, re.I) is None
        )

    def src_file_filter(self,filename):
        return filename.endswith('.ts') and not self.test_file_filter(filename)
