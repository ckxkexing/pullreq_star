from dateutil.relativedelta import relativedelta
from src.utils.utils import time_handler, str_handler
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
    # pr_before_merged / pr_before

    # get pr created_at 
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']

    sql = f'''
        select p.id, pmd.merge
        from prs p
        left join pr_merge_decision pmd
        on p.id = pmd.pr_id
        where p.closed_at < "{created_at}"
            and p.base_repo_id = {repo_id}
    '''

    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        all_pr_num = len(res)
        merge_pr_num = 0
        for pr in res:
            if pr['merge'] > 0:
                merge_pr_num += 1
        return {"pr_succ_rate":merge_pr_num/all_pr_num if all_pr_num else 0}


def stars(repo_id, pr_id):
    # in zhang's work, it is watcher count

    # get full name
    sql = f'''select full_name from projects where id = {repo_id}'''
    with conn:
        cursor.execute(sql)
        repo_name = cursor.fetchone()['full_name']
        owner, name = repo_name.split("/")

    # get repo_id in ghtorrent
    sql = f'''select id from users where login = '{owner}' '''
    gh_cursor.execute(sql)
    id = gh_cursor.fetchone()['id']
    sql = f'''select id from projects where owner_id={id} and name='{name}' '''
    gh_cursor.execute(sql)
    id = gh_cursor.fetchone()['id']

    # get pr created time
    sql = f'''select created_at from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        created_at = cursor.fetchone()['created_at']

    # get watcher count
    sql = f'''
        select count(w.user_id) as num_watchers
        from reduced_watchers w
        where w.created_at < '{created_at}'
            and w.repo_id = {id}
    '''
    gh_cursor.execute(sql)
    res = gh_cursor.fetchone()['num_watchers']
    return {"stars" : res}

def test_cases_per_kloc(repo_id, pr_id):
    pass

def perc_external_contribs(repo_id, pr_id, months_back=3):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']

    oldest = time_handler(created_at) - relativedelta(months=months_back)
    oldest = str_handler(oldest)

    # get core member list
    sql = f'''
        select user_id 
        from core_members c
        where project_id = {repo_id}
            and created_at < "{created_at}"
            and created_at >= "{oldest}"   
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        core_numbers = [u['user_id'] for u in res]
    core_numbers = set(core_numbers)
    # get github commit author list
    sql = f'''
        select author_id
        from project_commits pc, commits c
        where pc.commit_id = c.id
            and created_at < "{created_at}"
            and created_at >= "{oldest}" 
            and pc.project_id = {repo_id}
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        committer_numbers = [u['author_id'] for u in res]

    all_commit_num = len(committer_numbers)
    external_commit_num = 0
    for u in committer_numbers:
        if u not in core_numbers:
            external_commit_num += 1

    return {"perc_external_contribs" : external_commit_num / all_commit_num if all_commit_num else 0}

def team_size(repo_id, pr_id, months_back=3):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        user_id = res['creator_id']

    oldest = time_handler(created_at) - relativedelta(months=months_back)
    oldest = str_handler(oldest)

    sql = f'''
        select count(user_id) as team_size
        from core_members c
        where project_id = {repo_id}
            and created_at < "{created_at}"
            and created_at >= "{oldest}"
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        return {"team_size": res['team_size']}

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
    # get full name
    sql = f'''select full_name from projects where id = {repo_id}'''
    with conn:
        cursor.execute(sql)
        repo_name = cursor.fetchone()['full_name']
        owner, name = repo_name.split("/")

    # get repo_id in ghtorrent
    sql = f'''select id from users where login = '{owner}' '''
    gh_cursor.execute(sql)
    id = gh_cursor.fetchone()['id']
    sql = f'''select id from projects where owner_id={id} and name='{name}' '''
    gh_cursor.execute(sql)
    id = gh_cursor.fetchone()['id']
    # get pr created_at
    sql = f'''select created_at from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        created_at = cursor.fetchone()['created_at']

    # get fork count
    sql = f'''
        select count(*) as num_forks 
        from projects p
        where p.created_at < '{created_at}'
            and p.forked_from = {id}
    '''
    gh_cursor.execute(sql)
    res = gh_cursor.fetchone()['num_forks']
    return {"num_forks" : res}


def test_lines_per_kloc(repo_id, pr_id):
    pass

def asserts_per_kloc(repo_id, pr_id):
    pass

