from dbs.sqlite_base import conn, cursor

create_project_langs = """--sql
    create table IF NOT EXISTS project_langs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        lang TEXT,
        foreign key(project_id) references projects(id)
    );
"""

"""
NULL, :project_id, :lang
"""


def insert_project_langs(project_langs):
    sql = """
        INSERT INTO project_langs
        VALUES ( NULL, :project_id, :lang)
    """

    with conn:
        if type(project_langs) is list:
            cursor.executemany(sql, project_langs)
        else:
            cursor.execute(sql, project_langs)
