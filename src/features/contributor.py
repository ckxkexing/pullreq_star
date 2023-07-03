from dbs.sqlite_base import conn, cursor
from dbs.ghtorrent_base import gh_conn, gh_cursor

def bot_user(repo_id, pr_id):
    pass

def first_pr(repo_id, pr_id):
    pass

def core_member(repo_id, pr_id, months_back=None):
    # get pr created_at
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
    pass

def contrib_perc_commit(repo_id, pr_id):
    pass

def prior_review_num(repo_id, pr_id):
    pass

def prior_interaction(repo_id, pr_id):
    pass
