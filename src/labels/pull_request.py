from dbs.sqlite_base import get_sqlite_db_connection
from src.utils.utils import time_handler


def time_to_first_response(repo_id, pr_id):
    # as delay before comment
    # [bot, human, both]
    # return in mins
    conn, cursor = get_sqlite_db_connection()
    # get pr created time
    sql = f"""select created_at from prs where id = {pr_id}"""
    cursor.execute(sql)
    created_at = cursor.fetchone()["created_at"]

    sql = f"""--sql
        SELECT i.html_url , i.pr_id , ic.body , ic.creator_id ,ic.created_at
        from issues i
        join issue_comments ic
        on i.pr_id = {pr_id} and i.creator_id != ic.creator_id  and i.id = ic.issue_id
        order by ic.created_at
        limit 1
    ;"""
    cursor.execute(sql)
    res = cursor.fetchone()
    ttf = -1
    if res is not None:
        response_time = res["created_at"]
        c_t = time_handler(created_at)
        r_t = time_handler(response_time)

        ttf = divmod((r_t - c_t).total_seconds(), 60)[0]

    return {"time_to_first_response": ttf}


def time_to_handle(repo_id, pr_id):
    # as delay before comment
    # [bot, human, both]
    # return in mins
    conn, cursor = get_sqlite_db_connection()
    # get pr created time
    sql = f"""select created_at, closed_at from prs where id = {pr_id}"""
    cursor.execute(sql)
    res = cursor.fetchone()
    created_at = res["created_at"]
    closed_at = res["closed_at"]

    created_time = time_handler(created_at)
    closed_time = time_handler(closed_at)

    tth = divmod((closed_time - created_time).total_seconds(), 60)[0]

    return {"time_to_handle": tth}


def merge_decision(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    sql = f"""
        select merge
        from pr_merge_decision
        where pr_id = {pr_id}
    """
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        res = res["merge"] if res else 0

    return {"merge_decision": res}
