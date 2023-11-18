from dbs.sqlite_base import conn, cursor

create_pr_commits_of_file_touched = """--sql
    create table IF NOT EXISTS pr_commits_of_file_touched (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pr_id INTEGER,
        coft INTEGER,
        foreign key(pr_id) references prs(id)
    );
"""

"""
NULL, :pr_id, :coft
"""


def insert_pr_commits_of_file_touched(data):
    sql = """
        INSERT INTO pr_commits_of_file_touched
        VALUES ( NULL, :pr_id, :coft)
    """

    with conn:
        if type(data) is list:
            cursor.executemany(sql, data)
        else:
            cursor.execute(sql, data)
