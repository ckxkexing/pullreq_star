from dbs.sqlite_base import conn, cursor

create_prs = """--sql
    create table prs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        html_url TEXT,
        number INTEGER,
        state TEXT,
        locked INTEGER,
        title TEXT,
        body TEXT,
        creator_id INTEGER,
        created_at TEXT,
        updated_at TEXT,
        closed_at TEXT,
        merged_at TEXT,
        merge_commit_sha TEXT,
        draft INTEGER,
        base_repo_id INTEGER,
        base_label TEXT,
        base_ref TEXT,
        base_sha TEXT,
        head_label TEXT,
        head_ref TEXT,
        head_sha TEXT,
        foreign key(base_repo_id) references projects(id),
        foreign key(creator_id) references users(id)
    );
"""


def get_pr_by_pr_url(pr_url):
    with conn:
        cursor.execute("SELECT id FROM prs WHERE url=:url", {"url": pr_url})
        res = cursor.fetchone()
        return 0 if not res else res["id"]


def get_pr_by_number(repo_id, pr_number):
    with conn:
        cursor.execute(
            "SELECT id FROM prs WHERE base_repo_id=:base_repo_id and number=:number",
            {"base_repo_id": repo_id, "number": pr_number},
        )
        res = cursor.fetchone()
        return 0 if not res else res["id"]


def list_pr(repo_id):
    sql = f"""--sql
        select id, number, created_at, closed_at, html_url
        from prs p
        where p.base_repo_id = {repo_id};
    """
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        return res
