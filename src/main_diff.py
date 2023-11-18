import argparse
import re

import Levenshtein
from tqdm import tqdm
from transformers import RobertaTokenizer

from config.configs import repos
from dbs.mongo_base import mongo_db
from dbs.sqlite_base import get_sqlite_db_connection
from dbs.tables.projects import get_project_by_full_name
from dbs.tables.prs import list_pr
from src.utils.linguist import get_linguist

tokenizer = RobertaTokenizer.from_pretrained(
    "/data1/kexingchen/huggingface_models/microsoft_codebert-base"
)
max_source_length = 256


def similarity(a, b):
    ed = Levenshtein.distance(a, b)
    return 1 - ed / max(len(a), len(b))


def get_pr_commits(pr_id):

    conn, cursor = get_sqlite_db_connection()

    sql = f"""--sql
        select c.sha
            from prs
            left join pr_commits pc
            on prs.id = pc.pr_id
            left join commits c
            on pc.commit_id  = c.id
        where prs.id = {pr_id} and prs.created_at >= c.created_at
    ;"""

    with conn:
        cursor.execute(sql)
        commits = cursor.fetchall()
    return commits


def process_patch_lines(patch, linguist, diffs):
    adds = []
    rms = []
    pattern = r"@@ -(\d+),\d+ \+(\d+),\d+ @@"

    for line in patch.splitlines():
        if re.search(pattern, line) is not None:
            if len(rms) > 0 or len(adds) > 0:
                sim = similarity(rms, adds)
                if sim < 1:
                    diffs.append((sim, " ".join(rms), " ".join(adds)))
            rms = []
            adds = []
            continue

        if line.startswith("+") and len(line) < 1000:
            adds += linguist.tokenize(line[1:])
        if line.startswith("-") and len(line) < 1000:
            rms += linguist.tokenize(line[1:])
    return adds, rms


def parse_detail(detail, diffs):

    for file in detail["files"]:
        lang = file["filename"].split(".")[-1]
        linguist = get_linguist(lang)
        if not linguist or linguist.test_file_filter(file["filename"]):
            continue
        # only consider modified file
        if file["status"] != "modified" or "patch" not in file:
            continue

        adds = []
        rms = []
        adds, rms = process_patch_lines(file["patch"], linguist, diffs)

        if len(rms) > 0 or len(adds) > 0:
            sim = similarity(rms, adds)
            if sim < 1:
                diffs.append((sim, " ".join(rms), " ".join(adds)))


def get_pr_diff(pr):
    pr_id = pr["id"]
    col = mongo_db["commit_details"]
    diffs = []
    commits = get_pr_commits(pr_id)

    for commit in commits:
        sha = commit["sha"]
        query = {"commit": sha}
        details = col.find(query, {"_id": 0})
        for detail in details:
            parse_detail(detail, diffs)

    diffs.sort(key=lambda x: x[0] * -1)
    diff_rm = ""
    diff_add = ""
    cur_len = 0
    for sim, rm, add in diffs:
        if (
            cur_len + len(tokenizer.tokenize(add)) + len(tokenizer.tokenize(rm))
            <= max_source_length - 3
        ):
            diff_rm += rm
            diff_add += add
            cur_len += len(tokenizer.tokenize(add)) + len(tokenizer.tokenize(rm))
    return diff_rm, diff_add


if __name__ == "__main__":
    col = mongo_db["features"]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-o", dest="output_file")
    args = parser.parse_args()

    for owner, repo, lang in repos:
        print(f"{owner} / {repo}")
        repo_id = get_project_by_full_name(f"{owner}/{repo}")
        prs = list_pr(repo_id)
        for pr in tqdm(prs):
            diff_rm, diff_add = get_pr_diff(pr)
            if diff_rm == "" and diff_add == "":
                continue
            pr["code_add"] = diff_add
            pr["code_del"] = diff_rm
            key = {"id": pr["id"]}
            col.update_one(key, {"$set": pr}, upsert=True)
