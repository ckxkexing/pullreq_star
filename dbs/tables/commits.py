from dbs.sqlite_base import conn, cursor

create_commits = """--sql
    create table commits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sha TEXT UNIQUE,
        created_at TEXT,
        committed_at TEXT,
        message TEXT,
        tree_sha TEXT,
        tree_url TEXT,
        git_url TEXT,
        comment_count INTEGER,
        url TEXT,
        html_url TEXT,
        comments_url TEXT,
        author_id INTEGER,
        committer_id INTEGER,
        parents TEXT,
        foreign key(author_id) references users(id),
        foreign key(committer_id) references users(id)
    );
"""

"""
NULL,:sha, :created_at, :committed_at, :message,
    :tree_sha, :tree_url, :git_url, :comment_count,
    :url, :html_url, :comments_url, :author_id, :committer_id, :parents
"""


def insert_commits_list(items):
    sql = """--sql
        INSERT OR IGNORE INTO commits
        VALUES (
            NULL, :sha, :created_at, :committed_at, :message,
            :tree_sha, :tree_url, :git_url, :comment_count,
            :url, :html_url, :comments_url, :author_id, :committer_id, :parents
        );
    """
    with conn:
        return cursor.executemany(sql, items)


def insert_commits(item):
    sql = """--sql
        INSERT INTO commits
        VALUES (
            NULL, :sha, :created_at, :committed_at, :message,
            :tree_sha, :tree_url, :git_url, :comment_count,
            :url, :html_url, :comments_url, :author_id, :committer_id, :parents
        )
        RETURNING id;
    """

    with conn:
        return cursor.execute(sql, item).fetchone()["id"]


def get_commit_by_sha(sha):
    with conn:
        cursor.execute("SELECT id FROM commits WHERE sha=:sha", {"sha": sha})
        res = cursor.fetchone()
        return 0 if not res else res["id"]


def add_parents_column():
    # ALTER TABLE table_name
    #     ADD new_column_name column_definition;
    sql = """--sql
        ALTER TABLE commits
            ADD parents TEXT;
    """
    with conn:
        cursor.execute(sql)


def update_parents_many(items):
    sql = """--sql
        UPDATE commits SET parents=:parents WHERE id=:id ;
    """
    with conn:
        cursor.executemany(sql, items)
