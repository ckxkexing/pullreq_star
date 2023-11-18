# Copyright 2020-present Tae Hwan Jung
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import List

language_ext = {
    "python": [".py"],
    "javascript": [".js"],
    "go": [".go"],
    "java": [".java"],
    "ruby": [".rb"],
    "php": [".php"],
}

DOCSTRING_REGEX_TOKENIZER = re.compile(
    r"[^\s,'\"`.():\[\]=*;>{\}+-/\\]+|\\+|\.+|\(\)|{\}|\[\]|\(+|\)+|:+|\[+|\]+|{+|\}+|=+|\*+|;+|>+|\++|-+|/+"
)


def tokenize_docstring_from_string(docstr: str) -> List[str]:
    return [
        t
        for t in DOCSTRING_REGEX_TOKENIZER.findall(docstr)
        if t is not None and len(t) > 0
    ]


def tokenize_code(PARSER, blob: str) -> List:
    tokens = []
    tree = PARSER.parse(blob.encode())
    for child in tree.root_node.children:
        tokens += [t for t in tokenize_ast(child, blob) if t != ""]
    return tokens


def tokenize_ast(node, blob: str) -> List:
    tokens = []
    traverse(node, tokens)
    return [match_from_span(token, blob) for token in tokens]


def traverse(node, results: List) -> None:
    if "comment" in node.type:
        return
    if "string" in node.type:
        results.append(node)
        return
    for n in node.children:
        traverse(n, results)
    if not node.children:
        results.append(node)


def match_from_span(node, blob: str) -> str:
    lines = blob.split("\n")
    line_start = node.start_point[0]
    line_end = node.end_point[0]
    char_start = node.start_point[1]
    char_end = node.end_point[1]
    if line_start != line_end:
        return "\n".join(
            [lines[line_start][char_start:]]
            + lines[line_start + 1 : line_end]
            + [lines[line_end][:char_end]]
        )
    else:
        return lines[line_start][char_start:char_end]


def message_cleaner(message):
    if not message:
        return ""
    msg = message.split("---")[0]

    lines = []
    for line in msg.splitlines():
        if line.startswith("- [ ]"):
            continue
        pattern = r"^(#+) (.*)"
        if re.search(pattern, line):
            continue
        lines.append(line)
    msg = "\n".join(lines)

    msg = re.sub("(<!--.*?-->)", "", msg, flags=re.DOTALL)
    msg = re.sub("(<details>.*?</details>)", "", msg, flags=re.DOTALL)

    # remove code block
    msg = re.sub(r"```[^\S\r\n]*[a-z]*\n.*?\n```", "code-block", msg, 0, re.DOTALL)

    # change commit id to sha
    msg = re.sub(r"\b[0-9a-f]{7}\b|\b[0-9a-f]{40}\b", "commit-sha1", msg)

    # remove url
    msg = re.sub(r"https://github.com\S+", "gh-url", msg)
    msg = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", msg)
    msg = re.sub(r"https?:\S+", "", msg)

    lines = []
    for line in msg.splitlines():
        lin = line.strip()
        if not lin:
            continue
        lines.append(line)
    msg = "\n".join(lines)
    msg = re.sub(r"(\(|\[|\{|\<)#([0-9])+(\)|\]|\}|\>)", "", msg)
    msg = re.sub(r"#([0-9])+", "gh-url", msg)
    msg = re.sub(r"([0-9])+", "", msg)

    return msg
