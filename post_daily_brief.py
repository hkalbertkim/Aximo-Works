#!/usr/bin/env python3
"""
post_daily_brief.py

Runs daily_brief.py, captures its stdout, and posts it as a Linear comment
to a designated "Daily Brief" issue (e.g., HKA-38).

Env:
- LINEAR_API_KEY (Personal key; no Bearer)
"""

import os
import subprocess
import json
import urllib.request
from datetime import datetime


DAILY_BRIEF_ISSUE = "HKA-38"  # change if you create a new one


def die(msg: str, code: int = 1):
    raise SystemExit(f"ERROR: {msg}")


def gql(api_key: str, payload: dict) -> dict:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": api_key},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def post_comment(api_key: str, issue_id_or_identifier: str, body: str) -> str:
    query = """
    mutation($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment { id }
      }
    }
    """
    variables = {
        "input": {
            "issueId": issue_id_or_identifier,
            "body": body,
        }
    }
    res = gql(api_key, {"query": query, "variables": variables})
    if "errors" in res:
        die(json.dumps(res["errors"], ensure_ascii=False))
    data = res.get("data", {}).get("commentCreate", {})
    if not data.get("success"):
        die(f"commentCreate failed: {json.dumps(res, ensure_ascii=False)}")
    return data["comment"]["id"]


def main() -> int:
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        die("LINEAR_API_KEY not set. Run: export $(grep -v '^#' .env | xargs)")

    # Run daily_brief.py and capture stdout
    p = subprocess.run(
        ["python", "daily_brief.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        die(f"daily_brief.py failed:\n{p.stderr}")

    brief = p.stdout.strip()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = f"## Daily Brief ({ts})\n\n```\n{brief}\n```"

    comment_id = post_comment(api_key, DAILY_BRIEF_ISSUE, body)
    print(f"Posted daily brief comment to {DAILY_BRIEF_ISSUE}: commentId={comment_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
