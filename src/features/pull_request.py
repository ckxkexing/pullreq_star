from dbs.sqlite_base import conn, cursor

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
        return 0 if not res else res['before_commit_cnt']

def files_changed(repo_id, pr_id):
    pass

def files_added              (repo_id, pr_id):
    pass

def files_deleted            (repo_id, pr_id):
    pass

def churn_addition           (repo_id, pr_id):
    pass

def churn_deletion           (repo_id, pr_id):
    pass

def test_inclusion           (repo_id, pr_id):
    pass

def test_churn               (repo_id, pr_id):
    pass

def src_churn                (repo_id, pr_id):
    pass

def description_length       (repo_id, pr_id):
    pass

def commits_on_files_touched (repo_id, pr_id):
    pass
