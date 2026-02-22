#!/usr/bin/env python3
"""Post a concise EOD status comment to Linear."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime
from typing import Any

LINEAR_ENDPOINT = "https://api.linear.app/graphql"
DEFAULT_ISSUE = "HKA-38"
DEFAULT_NOTE = "EOD: committed & pushed; daily brief generated; email sent"


def _die(msg: str, code: int = 1) -> None:
    if code == 1:
        raise SystemExit(f"ERROR: {msg}")
    raise SystemExit(code)


def _is_dry_run() -> bool:
    return os.getenv("DRY_RUN", "0") == "1"


def _gql(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        LINEAR_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": api_key},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_comment(api_key: str, issue_id_or_identifier: str, body: str) -> str:
    query = """
    mutation($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment { id }
      }
    }
    """
    variables = {"input": {"issueId": issue_id_or_identifier, "body": body}}
    res = _gql(api_key, {"query": query, "variables": variables})
    if "errors" in res:
        _die(json.dumps(res["errors"], ensure_ascii=False))
    data = res.get("data", {}).get("commentCreate", {})
    if not data.get("success"):
        _die(f"commentCreate failed: {json.dumps(res, ensure_ascii=False)}")
    return str(data["comment"]["id"])


def main() -> int:
    dry_run = _is_dry_run()
    issue = os.getenv("EOD_LINEAR_ISSUE", DEFAULT_ISSUE)
    note = os.getenv("EOD_STATUS_NOTE", DEFAULT_NOTE)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = f"## EOD Update ({ts})\\n\\n{note}"

    if dry_run:
        print("DRY_RUN: would post Linear comment")
        print(f"DRY_RUN: issue={issue}")
        print(f"DRY_RUN: note={note}")
        print("DRY_RUN: required env vars: LINEAR_API_KEY")
        return 0

    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        _die("LINEAR_API_KEY not set")

    comment_id = _post_comment(api_key, issue, body)
    print(f"Posted EOD Linear comment to {issue}: commentId={comment_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
