import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.languages import *

def test_python():
    linguist = PythonData()
    filename = "tests/admin_custom_urls/models.py"
    assert linguist.test_file_filter(filename) == True


def test_java():
    linguist = JavaData()
    filename = "test/framework/src/main/java/org/elasticsearch/cli/CommandTestCase.java"
    assert linguist.test_file_filter(filename) == True

    filename = "server/src/main/java/org/elasticsearch/discovery/DiscoveryModule.java"
    assert linguist.test_file_filter(filename) == False

