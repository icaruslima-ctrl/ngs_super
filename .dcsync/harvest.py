#!/usr/bin/env python3
"""Scan the session transcript for inline DesignSync get_file results and write
each one to disk, so file contents make exactly one trip through the model.

Usage: harvest.py <transcript.jsonl> <dest-root>
"""
import base64
import json
import os
import re
import sys

transcript, root = sys.argv[1], sys.argv[2]
written = {}


def emit(payload):
    if payload.get("method") != "get_file" or "content" not in payload:
        return
    dest = os.path.join(root, payload["path"])
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if payload.get("isBase64"):
        with open(dest, "wb") as fh:
            fh.write(base64.b64decode(payload["content"]))
    else:
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(payload["content"])
    written[payload["path"]] = os.path.getsize(dest)


def walk(node):
    if isinstance(node, dict):
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)
    elif isinstance(node, str) and '"get_file"' in node:
        for match in re.finditer(r'\{"method":"get_file".*?"truncated":(?:true|false)\}', node, re.S):
            try:
                emit(json.loads(match.group(0)))
            except json.JSONDecodeError:
                pass


with open(transcript, "r", encoding="utf-8") as fh:
    for line in fh:
        try:
            walk(json.loads(line))
        except json.JSONDecodeError:
            continue

for path, size in sorted(written.items()):
    print(f"{size:>9}  {path}")
print(f"\n{len(written)} file(s) written to {root}")
