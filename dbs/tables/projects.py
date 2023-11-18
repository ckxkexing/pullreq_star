from dbs.sqlite_base import conn, cursor

create_projects = """--sql
    create table projects(
        id INTEGER  PRIMARY KEY AUTOINCREMENT,
        github_id INTEGER,
        full_name TEXT UNIQUE NOT NULL,
        html_url TEXT,
        created_at TEXT,
        default_branch TEXT
    );
"""


def insert_projects(project):
    with conn:
        return cursor.execute(
            """
            INSERT INTO projects VALUES (NULL, github_id, :full_name, :html_url, :created_at, :default_branch)
            RETURNING id;
            """,
            project,
        ).fetchone()["id"]


def get_project_by_full_name(full_name):
    with conn:
        cursor.execute(
            "SELECT id FROM projects WHERE full_name=:full_name",
            {"full_name": full_name},
        )
        res = cursor.fetchone()
        return 0 if not res else res["id"]
