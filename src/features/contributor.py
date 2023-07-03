from dateutil.relativedelta import relativedelta
from src.utils.utils import time_handler, str_handler
from dbs.sqlite_base import conn, cursor
from dbs.ghtorrent_base import gh_conn, gh_cursor

def bot_user(repo_id, pr_id):
    '''
       by account type
       or login name
       or manual check
    '''

    pass

def first_pr(repo_id, pr_id):
    # see in prev_pullreqs
    pass

def core_member(repo_id, pr_id, months_back=None):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        user_id = res['creator_id']

    sql = f'''--sql
        select user_id
        from core_members
        where project_id = {repo_id} 
            and created_at < "{created_at}"
            and user_id = {user_id}
    ;'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        flag = 0
        if len(res) > 0:
            flag = 1
        return {"core_member" : flag}

def social_strength(repo_id, pr_id):
    pass

def followers(repo_id, pr_id):
    # get user_id in ghtorrent
    sql = f'''
        select p.creator_id , u.login 
        from prs p , users u  
        where p.id = {pr_id} and p.creator_id = u.id 
    '''
    with conn:
        cursor.execute(sql)
        user_name = cursor.fetchone()['login']
    
    sql = f'''
        select id 
        from reduced_users r
        where r.login = '{user_name}'
    '''
    gh_cursor.execute(sql)
    user_id = gh_cursor.fetchone()['id']

    # get pr created_at
    sql = f'''select created_at from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        created_at = cursor.fetchone()['created_at']

    # get fork count
    sql = f'''
        select count(f.follower_id) as num_followers
        from reduced_followers f
        where f.user_id = {user_id}
        and f.created_at < '{created_at}'
    '''
    gh_cursor.execute(sql)
    res = gh_cursor.fetchone()['num_followers']
    return {"followers" : res}

def prev_pullreqs(repo_id, pr_id):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        user_id = res['creator_id']

    sql = f'''--sql
        select count(p.id) as cnt
        from prs p 
        where p.base_repo_id = {repo_id} and p.creator_id = {user_id} and p.created_at < "{created_at}"
    ;
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()['cnt']
        first_pr = 1 if res == 0 else 0
        return {"prev_pullreqs" : res, "first_pr" : first_pr}

def contrib_perc_commit(repo_id, pr_id):
    # % of previous contributor’s commit

    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        creator_id = res['creator_id']

    # get github commit author list
    sql = f'''
        select author_id
        from project_commits pc, commits c
        where pc.commit_id = c.id
            and created_at < "{created_at}"
            and pc.project_id = {repo_id}
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        committer_numbers = [u['author_id'] for u in res]

    all_commit_num = len(committer_numbers)
    contrib_commit_num = 0
    for u in committer_numbers:
        if u == creator_id:
            contrib_commit_num += 1

    return {"contrib_perc_commit" : contrib_commit_num / all_commit_num if all_commit_num else 0}

def prior_review_num(repo_id, pr_id):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        user_id = res['creator_id']

    sql = f'''
        select count(a.id) as prior_review_num
        from (
            select p.id, i.id as issue_id
            from prs p  
            join issues i on p.id = i.pr_id
            where p.base_repo_id = {repo_id} 
                and p.closed_at < '{created_at}'
                and p.created_at != {user_id}
        ) a 
        join issue_events ie on
        a.issue_id = ie.issue_id and (ie.event = 'merged' or ie.event = 'closed')
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        res = res['prior_review_num']
        return {"prior_review_num": res}


def prior_interaction(repo_id, pr_id):
    '''
      :prior_interaction => 
            r_prior_interaction_issue_events + r_prior_interaction_issue_comments +
            r_prior_interaction_pr_events + r_prior_interaction_pr_comments +
            r_prior_interaction_commits + r_prior_interaction_commit_comments,
    '''
    pass


def requester_succ_rate(repo_id, pr_id):
    # get pr created_at and creator_id
    sql = f'''select created_at, creator_id from prs where id = {pr_id}'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        created_at = res['created_at']
        user_id = res['creator_id']

    sql = f'''
        select p.id, pmd.merge
        from prs p
        left join pr_merge_decision pmd
        on p.id = pmd.pr_id
        where p.closed_at < "{created_at}"
            and p.creator_id = {user_id}
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
        return {"requester_succ_rate":merge_pr_num/all_pr_num if all_pr_num else 0}
