import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbs.ghtorrent_base import gh_conn, gh_cursor


def test_fetch():
    gh_cursor.execute("select * from users limit 1")
    data = gh_cursor.fetchall()
    assert len(data) == 1
