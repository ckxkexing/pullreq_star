import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.pull_request import at_mentions_in_description

def test_at_mention():
    body = "@aaa, review please"
    assert at_mentions_in_description(body) == 1

    body = "review please"
    assert at_mentions_in_description(body) == 0

    body = "@- please"
    assert at_mentions_in_description(body) == 0

    body = "lgtm, @merge-bot,@leader"
    assert at_mentions_in_description(body) == 2


    body = "contact me on aaa@gmail.com"
    assert at_mentions_in_description(body) == 0

    body = "@all contact me on aaa@gmail.com"
    assert at_mentions_in_description(body) == 1

    body = "merged.@bob"
    assert at_mentions_in_description(body) == 1

    body = "`@test` lgtm"
    assert at_mentions_in_description(body) == 0
