from dbs.sqlite_base import cursor, conn

create_pr_commits = '''--sql
    create table pr_commits(
        commit_id INTEGER NOT NULL,
        pr_id INTEGER NOT NULL,
        PRIMARY KEY(commit_id, pr_id),
        foreign key(commit_id) references commits(id),
        foreign key(pr_id) references prs(id)
    );
'''

'''
NULL, :commit_id, :pr_id
'''
def insert_pr_commit(item):
    sql = '''
        INSERT  OR IGNORE INTO pr_commits 
        VALUES (:commit_id, :pr_id)
    '''
    with conn:
        if type(item) is list:
            cursor.executemany(sql, item)
        else:
            cursor.execute(sql, item)    

