import re
import json
import argparse
from tqdm import tqdm
from config.configs import config
from config.configs import repos
from dbs.mongo_base import mongo_db
from dbs.tables.prs import list_pr
from dbs.tables.projects import get_project_by_full_name
from dbs.sqlite_base import get_sqlite_db_connection
from src.utils.languages.gitparser import message_cleaner

description_map = {}
def load_pr_desc(repo_id):
    conn, cursor = get_sqlite_db_connection()
    sql = f'''--sql
        WITH first_description_changes AS (
            SELECT pdc.pr_id, pdc.diff, ROW_NUMBER() OVER (PARTITION BY pdc.pr_id ORDER BY pdc.editedAt ASC) AS row_num
            FROM pr_description_changes pdc
        ), first_title_changes AS (
            SELECT ptc.pr_id, ptc.previousTitle, ROW_NUMBER() OVER (PARTITION BY ptc.pr_id ORDER BY ptc.createdAt ASC) AS row_num
            FROM pr_title_changes ptc
        ) 
        select p.id, COALESCE(pdc.diff, p.body) AS first_body,
                COALESCE(ptc.previousTitle, p.title) AS first_title
        from prs p 
        left join first_description_changes pdc on p.id = pdc.pr_id  AND pdc.row_num = 1
        left join first_title_changes ptc ON p.id = ptc.pr_id AND ptc.row_num = 1
        where p.base_repo_id = {repo_id};
    '''

    with conn:
        cursor.execute(sql)
        res = cursor.fetchall()
        for pr in tqdm(res):
            first_body = pr['first_body']
            first_title= pr['first_title']
            body = message_cleaner(first_body)
            title = message_cleaner(first_title)
            description_map[pr['id']] = body + ". " + title


def get_pr_desc(pr):
    pr_id = pr['id']
    return description_map[pr_id][:512]


if __name__ == "__main__":

    col = mongo_db['features']

    for owner, repo, lang in repos:
        print(f"{owner} / {repo}")
        repo_id = get_project_by_full_name(f"{owner}/{repo}")
        load_pr_desc(repo_id)

        prs = list_pr(repo_id)
        for pr in prs:
            description = get_pr_desc(pr)
            if description == "":
                continue
            pr['description'] = description
            key = {"id" : pr['id']}
            col.update_one(key, {"$set":pr}, upsert=True)
