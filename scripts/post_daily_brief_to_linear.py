#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

API = "https://api.linear.app/graphql"

def require_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        print("Missing .env. Create .env with LINEAR_API_KEY and LINEAR_TEAM_KEY.", file=sys.stderr)
        sys.exit(1)

def load_env_from_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k and k not in os.environ:
            os.environ[k] = v

def gql(query: str, variables=None):
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        raise RuntimeError("LINEAR_API_KEY is not set (env or .env).")

    payload = {"query": query, "variables": variables or {}}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        API,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key.strip(),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode("utf-8")
            out = json.loads(raw)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}\n{err_body}") from None

    if "errors" in out:
        raise RuntimeError(out["errors"])

    return out["data"]

def find_team_id(team_key: str) -> str:
    q = "query { teams { nodes { id key name } } }"
    teams = gql(q)["teams"]["nodes"]
    for t in teams:
        if t["key"] == team_key:
            return t["id"]
    raise RuntimeError(f"Team key '{team_key}' not found.")

def parse_identifier(identifier: str):
    if "-" not in identifier:
        raise RuntimeError(f"Invalid issue identifier: {identifier}")
    team_key, num = identifier.split("-", 1)
    try:
        number = int(num)
    except ValueError:
        raise RuntimeError(f"Invalid issue number in identifier: {identifier}")
    return team_key, number

def find_issue_id_by_team_and_number(team_id: str, number: int) -> str:
    # NOTE: In this Linear schema variant, number filter expects Float.
    q = """
    query($teamId: ID!, $num: Float!) {
      issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $num } }) {
        nodes { id identifier title number }
      }
    }
    """
    nodes = gql(q, {"teamId": team_id, "num": float(number)})["issues"]["nodes"]
    if not nodes:
        raise RuntimeError(f"Issue not found for teamId={team_id}, number={number}")
    return nodes[0]["id"]

def add_comment(issue_id: str, body: str) -> None:
    # NOTE: In this Linear schema variant, issueId input expects String (not ID).
    m = """
    mutation($id: String!, $body: String!) {
      commentCreate(input: { issueId: $id, body: $body }) { success }
    }
    """
    gql(m, {"id": issue_id, "body": body})

def main():
    repo_root = Path(__file__).resolve().parents[1]
    dotenv_path = repo_root / ".env"
    require_dotenv(dotenv_path)
    load_env_from_dotenv(dotenv_path)

    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", default="HKA-38", help="Issue identifier like HKA-38")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Comment body text")
    group.add_argument("--file", help="Path to text file")
    args = parser.parse_args()

    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")

    if not body or not body.strip():
        raise RuntimeError("Empty comment body.")

    configured_team_key = os.environ.get("LINEAR_TEAM_KEY")
    if not configured_team_key:
        raise RuntimeError("LINEAR_TEAM_KEY is not set (env or .env).")

    team_key, number = parse_identifier(args.issue)
    if team_key != configured_team_key:
        raise RuntimeError(
            f"Issue team '{team_key}' does not match LINEAR_TEAM_KEY '{configured_team_key}'."
        )
    team_id = find_team_id(team_key)
    issue_id = find_issue_id_by_team_and_number(team_id, number)
    add_comment(issue_id, body.strip())

    print(f"OK: posted comment to {args.issue} (team={team_key}).")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
