import re
import json
import threading
from dbs.sqlite_base import get_sqlite_db_connection
from src.utils.languages import *


def num_commits(repo_id, pr_id, at_open=True):
    conn, cursor = get_sqlite_db_connection()
    sql = f'''--sql
        select prs.id, prs.url, prs.html_url, count(prs.created_at >= c.created_at ) as before_commit_cnt
            from prs 
            left join pr_commits pc
            on prs.id = pc.pr_id 
            left join commits c 
            on pc.commit_id  = c.id 
        where prs.id = {pr_id}
        GROUP by prs.id
    ;'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        return {"num_commits": 0 if not res else res['before_commit_cnt']}

def files_level(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    # [files_changed, files_modified, files_added, files_deleted]
    sql = f'''--sql
        select cd.files 
        from prs 
        left join pr_commits pc
        on prs.id = pc.pr_id 
        left join commits c 
        on pc.commit_id  = c.id 
        left join commit_details cd 
        on c.id = cd.commit_id 
        where c.created_at <= prs.created_at AND prs.id = {pr_id}
    ;'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        files_modified, files_added, files_deleted = 0, 0, 0
        for files in res:
            files = files['files']
            if files is None: continue
            files = json.loads(files)
            for file in files:
                # https://stackoverflow.com/a/72849078
                if file['status'] == 'added':
                    files_added += 1
                elif file['status'] == 'removed':
                    files_deleted += 1
                else:
                    files_modified += 1
        return {"files_changed": files_modified + files_added + files_deleted,
                "files_added": files_added,
                "files_deleted": files_deleted,
                "files_modified": files_modified}


'''
churn_addition  : non-test lines add + test lines add
churn_deletion  : non-test lines deleted + test lines deleted
test_churn      : test lines add + test lines deleted
src_churn       : non-test lines add + non-test lines deleted
'''
def churn_level(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    # [churn_addition, churn_deletion, test_churn, src_churn, test_inclusion]
    lang_sql = f'''--sql
        select lang 
        from project_langs
        where project_id = {repo_id}
    ;
    '''
    with conn:
        cursor.execute(lang_sql)
        lang = cursor.fetchone()['lang']

    if re.match("javascript", lang, re.I):
        linguist = JavascriptData()
    elif re.match("python", lang, re.I):
        linguist = PythonData()
    elif re.match("dart", lang, re.I):
        linguist = DartData()
    elif re.match("go", lang, re.I):
        linguist = GoData()
    elif re.match("java", lang, re.I):
        linguist = JavaData()
    elif re.match("php", lang, re.I):
        linguist = PhpData()
    elif re.match("ruby", lang, re.I):
        linguist = RubyData()
    elif re.match("sass", lang, re.I):
        linguist = SassData()
    elif re.match("shell", lang, re.I):
        linguist = ShellData()
    elif re.match("typescript", lang, re.I):
        linguist = TypescriptData()
    elif lang == 'c':
        linguist = CData()
    elif lang == 'cu':
        linguist = CUData()
    elif lang == 'cpp':
        linguist = CPPData()

    sql = f'''--sql
        select cd.files 
        from prs 
        left join pr_commits pc
        on prs.id = pc.pr_id 
        left join commits c 
        on pc.commit_id  = c.id 
        left join commit_details cd 
        on c.id = cd.commit_id 
        where c.created_at <= prs.created_at AND prs.id = {pr_id}
    ;'''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        lines_add, test_lines_add = 0, 0
        lines_deleted, test_lines_deleted = 0, 0
        test_inclusion = 0

        for files in res:
            files = files['files']
            if files is None: continue
            files = json.loads(files)
            for file in files:
                if linguist.src_file_filter(file['filename']):
                    lines_add += file['additions']
                    lines_deleted += file['deletions']
                elif linguist.test_file_filter(file['filename']):
                    test_lines_add += file['additions']
                    test_lines_deleted += file['deletions']

                    if file['additions'] > 0:
                        test_inclusion += 1

        return {"churn_addition": lines_add + test_lines_add,
                "churn_deletion": lines_deleted + test_lines_deleted,
                "test_churn": test_lines_add + test_lines_deleted,
                "src_churn": lines_add + test_lines_add,
                "test_inclusion": test_inclusion 
                }


def description_length(repo_id, pr_id, at_open=True):
    conn, cursor = get_sqlite_db_connection()

    sql = f'''--sql
        select body
        from pr_description_first_version
        where pr_id = {pr_id};
    '''
    cursor.execute(sql)
    res = cursor.fetchone()
    return {"description_length": len(res['body']) if res['body'] else 0}


def commits_on_files_touched(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    sql = '''
        select coft 
        from pr_commits_of_file_touched
        where pr_id = ?
    '''

    with conn:
        cursor.execute(sql, (pr_id, ))
        res = cursor.fetchone()
        res = res['coft'] if res else 0

    return {"coft" : res}

def merge_decision(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    sql = f'''
        select merge
        from pr_merge_decision
        where pr_id = {pr_id}
    '''
    with conn:
        cursor.execute(sql)
        res = cursor.fetchone()
        res = res['merge'] if res else 0

    return {'merge_decision': res}

# Find at_mention in text
# Num of @uname mentions in the description(title doesn't take effect)
# Modelling the results of: An Exploratory Study of @-mention in GitHub's Pull-requests
# DOI: 10.1109/APSEC.2014.58
def at_mentions_in_description(body):
    count = len(re.findall(r'@(?!\-)([a-zA-Z0-9\-]+)(?<!\-)', re.sub(r'`.*?`', '', re.sub(r'[\w]*@[\w]+\.[\w]+', '', body))))
    return count

def at_tag_in_description(repo_id, pr_id):
    conn, cursor = get_sqlite_db_connection()
    sql = f'''--sql
        select body, title
        from pr_description_first_version
        where pr_id = {pr_id};
    '''
    cursor.execute(sql)
    res = cursor.fetchone()
    return {"at_mentions_in_description": at_mentions_in_description(res['body']) if res['body'] else 0}


def find_links(body):
    if type(body) is not str:
        return []
    matches = re.findall(r'#([0-9]+)', body)
    return matches


def backward_link(repo_id, pr_id):
    '''
        [backward_issue_link, backward_pr_link]
    '''
    conn, cursor = get_sqlite_db_connection()
    sql = f'''--sql
        select body, title
        from pr_description_first_version
        where pr_id = {pr_id};
    '''
    cursor.execute(sql)
    res = cursor.fetchone()
    github_numbers = find_links(res['body'])

    issue_link_cnt, pr_link_cnt = 0, 0

    for number in set(github_numbers):
        sql = f'''--sql
            select id, pr_id
            from issues i
            where i.project_id = {repo_id} and i.number = {number}
        ;'''
        cursor.execute(sql)
        res = cursor.fetchone()
        if res is not None and res['id'] :
            if res['pr_id'] == 0:
                issue_link_cnt += 1
            else :
                pr_link_cnt += 1

    return {"backward_issue_link":issue_link_cnt, "backward_pr_link":pr_link_cnt}
