from dbs.sqlite_base import get_sqlite_db_connection
import random
from tools.file_util import write_csv_data
from config.configs import config
import pandas as pd

random.seed(1)
conn, cursor = get_sqlite_db_connection()


def get_project_by_full_name(full_name):
    with conn:
        cursor.execute(
            "SELECT id FROM projects WHERE full_name=:full_name",
            {"full_name": full_name},
        )
        res = cursor.fetchone()
        return 0 if not res else res["id"]


def get_pr_by_number(repo_id, pr_number):
    with conn:
        cursor.execute(
            "SELECT id FROM prs WHERE base_repo_id=:base_repo_id and number=:number",
            {"base_repo_id": repo_id, "number": pr_number},
        )
        res = cursor.fetchone()
        return 0 if not res else res["id"]


def get_labels_by_pr(pr_id):
    with conn:
        cursor.execute(
            "SELECT name, url, description FROM pr_labels WHERE pr_id=:pr_id",
            {"pr_id": pr_id},
        )
        res = cursor.fetchall()
        return [] if not res else res


if __name__ == "__main__":

    release_pr = pd.read_csv(f"{config['raw_data']}/my_new_pullreq_Releated_to_release_note.csv")
    header = ["name", "url", "description"]
    res = []
    exist_name = {}
    for pr in release_pr["html_url"]:
        # https://github.com/atom/atom/pull/22769
        number = pr.split("/")[-1]
        owner = pr.split("/")[-4]
        repo = pr.split("/")[-3]

        repo_id = get_project_by_full_name(f"{owner}/{repo}")
        pr_id = get_pr_by_number(repo_id, number)
        labels = get_labels_by_pr(pr_id)
        for label in labels:
            if label["name"] in exist_name:
                continue
            exist_name[label["name"]] = 1
            res.append([
                label["name"],
                label["url"],
                label["description"]
            ])

    write_csv_data("sample_tag_label_in_released_pr.csv", header, res)
