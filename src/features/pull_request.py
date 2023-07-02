import re
import json
from dbs.sqlite_base import conn, cursor
from src.utils.languages import *

def num_commits(repo_id, pr_id, at_open=True):
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
        linguist = typescript()
    elif re.match("c", lang, re.I):
        linguist = CCData()

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


global_description_length_map = {}
global_description_length_ssid = 0
def description_length(repo_id, pr_id, at_open=True):
    global global_description_length_ssid, global_description_length_map
    sql = f'''--sql
        WITH first_description_changes AS (
            SELECT pdc.pr_id, pdc.diff, ROW_NUMBER() OVER (PARTITION BY pdc.pr_id ORDER BY pdc.editedAt ASC) AS row_num
            FROM pr_description_changes pdc
        ), first_title_changes AS (
            SELECT ptc.pr_id, ptc.previousTitle, ROW_NUMBER() OVER (PARTITION BY ptc.pr_id ORDER BY ptc.createdAt ASC) AS row_num
            FROM pr_title_changes ptc
        ) 
        select p.id, COALESCE(pdc.diff, p.body) AS first_body, p.body as body,
                COALESCE(ptc.previousTitle, p.title) AS first_title, p.title as title
        from prs p 
        left join first_description_changes pdc on p.id = pdc.pr_id  AND pdc.row_num = 1
        left join first_title_changes ptc ON p.id = ptc.pr_id AND ptc.row_num = 1
        where p.base_repo_id = {repo_id};
    '''
    if global_description_length_ssid != repo_id:
        with conn:
            cursor.execute(sql)
            res = cursor.fetchall()
            global_description_length_ssid = repo_id
            for pr in res:
                global_description_length_map[pr['id']] = len(pr['first_body']) if pr['first_body'] else 0
    return {"description_length": global_description_length_map[pr_id] if pr_id in global_description_length_map else 0}


def commits_on_files_touched (repo_id, pr_id):
    pass
