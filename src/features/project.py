from src.utils.utils import time_handler
from dbs.sqlite_base import conn, cursor

from dbs.ghtorrent_base import gh_conn, gh_cursor

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

def test_cases_per_kloc(repo_id, pr_id):
    pass

def perc_external_contribs(repo_id, pr_id):
    pass

def team_size(repo_id, pr_id):
    pass

def open_issue_num(repo_id, pr_id):
    sql = '''--sql
        SELECT
            SUM(CASE WHEN issues.created_at < (SELECT created_at FROM prs WHERE id = ?) THEN 1 ELSE 0 END) AS opened_num,
            SUM(CASE WHEN issues.closed_at is not NULL and issues.closed_at < (SELECT created_at FROM prs WHERE id = ?) THEN 1 ELSE 0 END) AS closed_num
        FROM
            issues
        WHERE
            issues.project_id = ? AND
            issues.pr_id = 0
    ;
    '''
    with conn:
        cursor.execute(sql, (pr_id, pr_id, repo_id))
        result = cursor.fetchone()
        opened_num = result['opened_num']
        closed_num = result['closed_num']
        return {"open_issue_num": opened_num - closed_num}


def open_pr_num(repo_id, pr_id):
    sql = '''--sql
        SELECT
            SUM(CASE WHEN issues.created_at < (SELECT created_at FROM prs WHERE id = ?) THEN 1 ELSE 0 END) AS opened_num,
            SUM(CASE WHEN issues.closed_at is not NULL and issues.closed_at < (SELECT created_at FROM prs WHERE id = ?) THEN 1 ELSE 0 END) AS closed_num
        FROM
            issues
        WHERE
            issues.project_id = ? AND
            issues.pr_id > 0
    ;
    '''
    with conn:
        cursor.execute(sql, (pr_id, pr_id, repo_id))
        result = cursor.fetchone()
        opened_num = result['opened_num']
        closed_num = result['closed_num']
        return {"open_pr_num": opened_num - closed_num}


def fork_num(repo_id, pr_id):
    sql = '''select * from projects limit 5;'''
    gh_cursor.execute(sql)
    result = gh_cursor.fetchall()
    for res in result:
        print(res)
    return {}
    sql = '''--sql
        select count(*) as num_forks 
        from projects p
        where p.created_at < ? 
        and p.forked_from = ?
    ;'''
    pass

def test_lines_per_kloc(repo_id, pr_id):
    pass

def asserts_per_kloc(repo_id, pr_id):
    pass

def requester_succ_rate(repo_id, pr_id):
    pass
