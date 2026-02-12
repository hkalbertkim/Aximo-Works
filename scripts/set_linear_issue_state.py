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
        headers={"Content-Type": "application/json", "Authorization": api_key.strip()},
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
    q = """
    query($teamId: ID!, $num: Float!) {
      issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $num } }) {
        nodes { id identifier title number state { name } }
      }
    }
    """
    nodes = gql(q, {"teamId": team_id, "num": float(number)})["issues"]["nodes"]
    if not nodes:
        raise RuntimeError(f"Issue not found for teamId={team_id}, number={number}")
    return nodes[0]["id"]

def find_state_id(team_id: str, state_name: str) -> str:
    q = """
    query($teamId: String!) {
      team(id: $teamId) {
        states { nodes { id name } }
      }
    }
    """
    states = gql(q, {"teamId": team_id})["team"]["states"]["nodes"]
    for s in states:
        if s["name"].lower() == state_name.lower():
            return s["id"]
    raise RuntimeError(f"State '{state_name}' not found. Available: {[s['name'] for s in states]}")

def set_issue_state(issue_id: str, state_id: str) -> None:
    # NOTE: In some Linear schema variants, ids are treated as String. We'll pass as String to be safe.
    m = """
    mutation($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) { success }
    }
    """
    gql(m, {"id": issue_id, "stateId": state_id})

def main():
    repo_root = Path(__file__).resolve().parents[1]
    dotenv_path = repo_root / ".env"
    require_dotenv(dotenv_path)
    load_env_from_dotenv(dotenv_path)

    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, help="Issue identifier like HKA-73")
    ap.add_argument("--state", required=True, help="Target state name, e.g., Done / In Progress / Todo")
    args = ap.parse_args()

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
    state_id = find_state_id(team_id, args.state)
    set_issue_state(issue_id, state_id)

    print(f"OK: set {args.issue} -> {args.state}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
