#!/usr/bin/env python3
"""
daily_brief.py — Linear Daily Brief (AXIMO style)

Outputs:
- What should I do today?  (Todo + In Progress grouped by project)
- What did we decide?      (Issues moved to Done recently — lightweight proxy)
- What is at risk next?    (Old In Progress + high-count Backlog per project)

Notes:
- Uses LINEAR_API_KEY from env (Personal key; no Bearer).
- Uses linear_routing.json for Team + Project + State IDs.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parent
ROUTING_PATH = ROOT / "linear_routing.json"


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def gql(api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": api_key},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def load_routing() -> Dict[str, Any]:
    if not ROUTING_PATH.exists():
        die(f"Missing {ROUTING_PATH}")
    return json.loads(ROUTING_PATH.read_text(encoding="utf-8"))


def fetch_issues(api_key: str, project_id: str, state_ids: List[str], first: int = 50) -> List[Dict[str, Any]]:
    # Linear supports filter by project + state
    query = """
    query($filter: IssueFilter, $first: Int) {
      issues(filter: $filter, first: $first, orderBy: updatedAt) {
        nodes {
          id
          identifier
          title
          url
          updatedAt
          createdAt
          state { id name type }
          project { id name }
        }
      }
    }
    """
    variables = {
        "first": first,
        "filter": {
            "project": {"id": {"eq": project_id}},
            "state": {"id": {"in": state_ids}},
        },
    }
    res = gql(api_key, {"query": query, "variables": variables})
    if "errors" in res:
        die(json.dumps(res["errors"], ensure_ascii=False))
    return res["data"]["issues"]["nodes"]


def iso_to_dt(s: str) -> datetime:
    # Linear returns ISO8601; parse minimally
    # Example: "2026-02-08T15:44:12.345Z"
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt_issue(i: Dict[str, Any]) -> str:
    return f"- {i['identifier']} {i['title']} ({i['url']})"


def main() -> int:
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        die("LINEAR_API_KEY not set. Run: export $(grep -v '^#' .env | xargs)")

    routing = load_routing()
    projects = routing["projects"]
    states = routing["states"]

    sid_backlog = states["backlog"]
    sid_todo = states["todo"]
    sid_inprog = states["in_progress"]
    sid_done = states["done"]

    # Collect per project
    now = datetime.now(timezone.utc)

    todo_blocks: List[str] = []
    decided_blocks: List[str] = []
    risk_blocks: List[str] = []

    for pname, pid in projects.items():
        todos = fetch_issues(api_key, pid, [sid_todo, sid_inprog], first=50)
        dones = fetch_issues(api_key, pid, [sid_done], first=20)
        backlogs = fetch_issues(api_key, pid, [sid_backlog], first=50)

        # What should I do today?
        if todos:
            todo_blocks.append(f"\n{pname}\n" + "\n".join(fmt_issue(i) for i in reversed(todos[-10:])))

        # What did we decide? (proxy = recently updated Done)
        recent_done = []
        for i in dones:
            if (now - iso_to_dt(i["updatedAt"])).days <= 7:
                recent_done.append(i)
        if recent_done:
            decided_blocks.append(f"\n{pname}\n" + "\n".join(fmt_issue(i) for i in reversed(recent_done[-10:])))

        # What is at risk next?
        risks = []

        # (1) 오래 끌리는 In Progress
        inprog = [i for i in todos if i["state"]["id"] == sid_inprog]
        for i in inprog:
            age_days = (now - iso_to_dt(i["updatedAt"])).days
            if age_days >= 3:
                risks.append((age_days, i, "Stale In Progress"))

        # (2) Backlog 폭증
        if len(backlogs) >= 20:
            risks.append((len(backlogs), {"identifier": "", "title": f"Backlog count is {len(backlogs)} (needs triage)", "url": ""}, "Backlog pile-up"))

        if risks:
            lines = []
            for score, item, tag in sorted(risks, key=lambda x: x[0], reverse=True)[:10]:
                if item.get("identifier"):
                    lines.append(f"- [{tag}] {item['identifier']} {item['title']} ({item['url']})")
                else:
                    lines.append(f"- [{tag}] {item['title']}")
            risk_blocks.append(f"\n{pname}\n" + "\n".join(lines))

    print("WHAT SHOULD I DO TODAY?")
    print("\n".join(todo_blocks) if todo_blocks else "\n- (none)")

    print("\n\nWHAT DID WE DECIDE? (last 7 days done)")
    print("\n".join(decided_blocks) if decided_blocks else "\n- (none)")

    print("\n\nWHAT IS AT RISK NEXT?")
    print("\n".join(risk_blocks) if risk_blocks else "\n- (none)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
