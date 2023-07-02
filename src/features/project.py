from src.utils.utils import time_handler
from dbs.sqlite_base import conn, cursor

def sloc(repo_id, pr_id):
    pass

def project_age(repo_id, pr_id):
    sql = f'''--sql
        select (strftime('%Y', prs.created_at) - STRFTIME('%Y', p.created_at)) * 12 + strftime('%m', prs.created_at) - STRFTIME('%m', p.created_at) AS project_age
        from prs 
        left join projects p 
        on prs.base_repo_id  = p.id 
        where prs.id = {pr_id}
    ;'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        return {'project_age': 0 if not res else res['project_age']}

def pushed_delta(repo_id, pr_id):
    # in hours

    previous_sql = f"""--sql
        SELECT created_at
        FROM prs
        WHERE prs.base_repo_id={repo_id}  and created_at < (SELECT created_at FROM prs WHERE id = {pr_id})
        ORDER BY created_at DESC
        LIMIT 1;
    """

    current_sql = f"""--sql
        SELECT created_at
        FROM prs
        WHERE id = {pr_id}
    ;
    """
    with conn:
        cursor.execute(previous_sql)
        res1 = cursor.fetchone()
        if not res1:
            return {"pushed_delta": 0}
        previous_created_at = time_handler(res1['created_at'])

        cursor.execute(current_sql)
        res2 = cursor.fetchone()
        current_created_at = time_handler(res2['created_at'])
        return {"pushed_delta": divmod((current_created_at - previous_created_at).total_seconds(), 3600)[0]}

def pr_succ_rate(repo_id, pr_id):
    pass

def stars(repo_id, pr_id):
    pass

def test_cases_per_kloc (repo_id, pr_id):
    pass

def perc_external_contri(repo_id, pr_id):
    pass

def team_size(repo_id, pr_id):
    pass

def open_issue_num(repo_id, pr_id):
    pass

def open_pr_num(repo_id, pr_id):
    pass

def fork_num(repo_id, pr_id):
    pass

def test_lines_per_kloc(repo_id, pr_id):
    pass

def asserts_per_kloc(repo_id, pr_id):
    pass

def requester_succ_rate(repo_id, pr_id):
    pass
