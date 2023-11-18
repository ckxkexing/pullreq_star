class Lang:
    def test_file_filter():
        pass

    def src_file_filter():
        pass


def strip_c_style_comments(line):
    """keep // remove"""
    res = ""
    pre = ""
    for i in line:
        if pre == i and i == "/":
            pre = ""
            break
        res += pre
        pre = i
    res += pre
    return res
