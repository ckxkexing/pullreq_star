from src.features.pull_request import first_comment_time
from src.features.pull_request import num_comments
from src.features.pull_request import list_comments
from src.features.pull_request import num_tag_labels

def test_sql():
    rr = list_comments(1, 1)

    res = first_comment_time(1, 1)
    print(res)

    res2 = num_comments(1, 1)
    print(res2)

    print(num_tag_labels(30, 5315))

if __name__ == "__main__":
    test_sql()
