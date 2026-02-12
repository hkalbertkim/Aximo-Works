#!/usr/bin/env python3
"""
linear_cli.py — Stable v1.0

Purpose
- Create Linear issues from stdin (clipboard, files, pipes)
- Route to correct Project by [PROJECT] prefix
- Prevent garbage issues from terminal noise

Usage
  # Single issue
  python linear_cli.py create --project AXIMO --title "[AXIMO] Fix X"

  # Intake from clipboard / pipe
  pbpaste | python linear_cli.py intake --state backlog

Requirements
- Env var: LINEAR_API_KEY (Personal API key, NO Bearer)
- File: linear_routing.json (team, projects, states)
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
ROUTING_PATH = ROOT / "linear_routing.json"


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_routing() -> Dict[str, Any]:
    if not ROUTING_PATH.exists():
        die(f"Missing {ROUTING_PATH}. Create it first.")
    return json.loads(ROUTING_PATH.read_text(encoding="utf-8"))


def gql(api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key,  # Personal API key (no Bearer)
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


# -------------------------------------------------------------------
# Linear ops
# -------------------------------------------------------------------
def create_issue(
    api_key: str,
    team_id: str,
    project_id: str,
    state_id: str,
    title: str,
    description: Optional[str] = None,
) -> Tuple[str, str, str]:
    query = """
    mutation($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue { identifier title url }
      }
    }
    """
    variables = {
        "input": {
            "teamId": team_id,
            "projectId": project_id,
            "stateId": state_id,
            "title": title,
        }
    }
    if description:
        variables["input"]["description"] = description

    res = gql(api_key, {"query": query, "variables": variables})
    if "errors" in res:
        die(json.dumps(res["errors"], ensure_ascii=False))
    data = res.get("data", {}).get("issueCreate", {})
    if not data.get("success"):
        die(f"Issue creation failed: {json.dumps(res, ensure_ascii=False)}")

    issue = data["issue"]
    return issue["identifier"], issue["title"], issue["url"]

def update_issue_state(api_key: str, issue_id_or_identifier: str, state_id: str) -> Tuple[str, str, str]:
    """
    Update issue state by Linear issue ID or identifier (e.g., 'HKA-28').
    Returns (identifier, new_state_name, url).
    """
    query = """
    mutation($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue { id identifier url state { id name } }
      }
    }
    """
    variables = {"id": issue_id_or_identifier, "input": {"stateId": state_id}}
    res = gql(api_key, {"query": query, "variables": variables})
    if "errors" in res:
        die(json.dumps(res["errors"], ensure_ascii=False))
    data = res.get("data", {}).get("issueUpdate", {})
    if not data.get("success"):
        die(f"Issue update failed: {json.dumps(res, ensure_ascii=False)}")
    issue = data["issue"]
    return issue["identifier"], issue["state"]["name"], issue["url"]


# -------------------------------------------------------------------
# Intake parsing (SAFE)
# -------------------------------------------------------------------
def parse_intake_lines(text: str) -> List[Tuple[str, str]]:
    """
    One line = one issue

    Accepted:
      [AXIMO] title...
      [VIVIDO] title...

    Safety:
    - Ignore empty lines
    - Ignore shell prompts, commands, URLs, prior CLI output
    - Default untagged lines to AXIMO
    """

    items: List[Tuple[str, str]] = []

    def is_noise(line: str) -> bool:
        l = line.strip()
        if not l:
            return True
        if l.startswith("#"):
            return True
        if l.startswith("("):  # (.venv) user@host %
            return True
        if l.startswith("%"):
            return True
        if "https://linear.app/" in l:
            return True
        lower = l.lower()
        for p in (
            "pbpaste",
            "sed ",
            "cd ",
            "ls ",
            "export ",
            "source ",
            "python ",
            "./",
        ):
            if lower.startswith(p):
                return True
        return False

    for raw in text.splitlines():
        line = raw.strip()
        if is_noise(line):
            continue

        if line.startswith("[") and "]" in line:
            proj = line[1: line.index("]")].strip().upper()
            title = line[line.index("]") + 1 :].strip()
            if proj and title:
                if not title.startswith(f"[{proj}]"):
                    title = f"[{proj}] {title}"
                items.append((proj, title))
                continue

        # Fallback
        items.append(("AXIMO", line))

    return items

def parse_project_and_state(line: str) -> Tuple[str, Optional[str], str]:
    """
    Accept formats:
      [AXIMO] title...
      [AXIMO][TODO] title...
      [VIVIDO][BACKLOG] title...
      [SINGSYNC][IN_PROGRESS] title...

    Returns: (project, state_or_none, normalized_title)
    """
    s = line.strip()

    project = "AXIMO"
    state = None
    title = s

    # Extract first bracket (project)
    if s.startswith("[") and "]" in s:
        first = s[1: s.index("]")].strip().upper()
        rest = s[s.index("]") + 1 :].strip()
        if first:
            project = first
            title = rest

    # Extract optional second bracket (state)
    if title.startswith("[") and "]" in title:
        second = title[1: title.index("]")].strip().upper()
        rest2 = title[title.index("]") + 1 :].strip()
        # Map state aliases
        alias = {
            "BACKLOG": "backlog",
            "TODO": "todo",
            "IN_PROGRESS": "in_progress",
            "DOING": "in_progress",
            "DONE": "done",
        }
        if second in alias and rest2:
            state = alias[second]
            title = rest2

    # Ensure title includes [PROJECT] prefix for readability in Linear
    if not title.startswith(f"[{project}]"):
        title = f"[{project}] {title}"

    return project, state, title


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create a single issue")
    p_create.add_argument("--project", required=True)
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--state", default=None)

    p_intake = sub.add_parser("intake", help="Create many issues from stdin")
    p_intake.add_argument("--state", default=None)

    p_move = sub.add_parser("move", help="Move an issue to a workflow state")
    p_move.add_argument("--issue", required=True, help="Issue identifier (e.g., HKA-28) or issue ID")
    p_move.add_argument("--state", required=True, help="backlog|todo|in_progress|done")


    args = parser.parse_args()

    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        die("LINEAR_API_KEY not set. Run: export $(grep -v '^#' .env | xargs)")

    routing = load_routing()
    team_id = routing["team"]["id"]
    projects = routing["projects"]
    states = routing["states"]
    default_state = routing.get("defaults", {}).get("initial_state", "backlog")

    def state_id(name: Optional[str]) -> str:
        n = (name or default_state).lower()
        if n not in states:
            die(f"Unknown state '{n}'. Valid: {', '.join(states.keys())}")
        return states[n]

    if args.cmd == "create":
        proj = args.project.upper()
        if proj not in projects:
            die(f"Unknown project '{proj}'. Valid: {', '.join(projects.keys())}")
        sid = state_id(args.state)
        ident, title, url = create_issue(
            api_key, team_id, projects[proj], sid, args.title
        )
        print(f"{proj}: {ident} {url}")
        return 0
    
    if args.cmd == "move":
        sid = state_id(args.state)
        ident, new_state, url = update_issue_state(api_key, args.issue, sid)
        print(f"{ident}: moved to {new_state} {url}")
        return 0


    if args.cmd == "intake":
        sid = state_id(args.state)
        text = sys.stdin.read()
        items = parse_intake_lines(text)

        if len(items) < 1:
            die("No valid intake lines found. Clipboard empty or filtered.")

        for proj, raw_title in items:
            proj_u, state_override, title = parse_project_and_state(raw_title)
            pid = projects.get(proj_u, projects["AXIMO"])
            sid2 = state_id(state_override) if state_override else sid
            ident, t, url = create_issue(api_key, team_id, pid, sid2, title)
            print(f"{proj_u}: {ident} {url}")

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
