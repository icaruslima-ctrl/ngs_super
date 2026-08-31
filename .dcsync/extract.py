#!/usr/bin/env python3
"""Decode a persisted DesignSync get_file tool result into a real file on disk.

Usage: extract.py <tool-result.json> <dest-path>
"""
import base64
import json
import os
import sys

src, dest = sys.argv[1], sys.argv[2]

with open(src, "r", encoding="utf-8") as fh:
    payload = json.load(fh)

content = payload["content"]
os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

if payload.get("isBase64"):
    with open(dest, "wb") as fh:
        fh.write(base64.b64decode(content))
else:
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(content)

if payload.get("truncated"):
    sys.exit(f"WARNING: {payload['path']} was truncated by the 256 KiB cap")

print(f"{dest}  ({os.path.getsize(dest)} bytes)")
