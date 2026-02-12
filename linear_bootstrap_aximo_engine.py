import os, json, urllib.request

API = "https://api.linear.app/graphql"

def gql(query: str, variables=None):
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        raise RuntimeError("LINEAR_API_KEY is not set")
    payload = {"query": query, "variables": variables or {}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": api_key},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        out = json.loads(r.read().decode("utf-8"))
    if "errors" in out:
        raise RuntimeError(out["errors"])
    return out["data"]

def find_team_by_key(team_key: str):
    q = "query { teams { nodes { id key name } } }"
    teams = gql(q)["teams"]["nodes"]
    for t in teams:
        if t["key"] == team_key:
            return t
    raise RuntimeError(f"Team key '{team_key}' not found. Available: {[t['key'] for t in teams]}")

def find_state(team_id: str, state_name: str):
    q = """
    query($teamId: String!) {
      team(id: $teamId) { states { nodes { id name type } } }
    }
    """
    states = gql(q, {"teamId": team_id})["team"]["states"]["nodes"]
    for s in states:
        if s["name"].lower() == state_name.lower():
            return s
    raise RuntimeError(f"State '{state_name}' not found. Available: {[s['name'] for s in states]}")

def create_issue(team_id: str, title: str, description: str, state_id: str):
    m = """
    mutation($input: IssueCreateInput!) {
      issueCreate(input: $input) { success issue { id identifier url title } }
    }
    """
    data = gql(m, {"input": {"teamId": team_id, "title": title, "description": description, "stateId": state_id}})
    return data["issueCreate"]["issue"]

def main():
    team_key = os.environ.get("LINEAR_TEAM_KEY", "HKA")
    epic_title = "Aximo Engine v0 – Local AI Infrastructure"

    team = find_team_by_key(team_key)
    todo = find_state(team["id"], "Todo")
    inprog = find_state(team["id"], "In Progress")

    epic = create_issue(
        team["id"],
        f"[AXIMO] {epic_title}",
        "\n".join([
            "Goal: Local-first AI engine to remove LLM limits and differentiate from OpenClaw.",
            "",
            "Deliverables:",
            "- Local LLM runtime on M1 Max",
            "- DeepSeek Coder local integration",
            "- Model routing layer (Local-first, Frontier fallback)",
            "- Memory Core v0 schema (event/graph/temporal/approval)",
        ]),
        todo["id"],
    )

    issues = [
        ("[AXIMO] Setup Local LLM Runtime (M1 Max)",
         "- Install Ollama\n- Start background service\n- Confirm API health check\n",
         inprog["id"]),
        ("[AXIMO] Integrate DeepSeek Coder (local)",
         "- Pull deepseek-coder:6.7b\n- Benchmark response time\n- Validate coding output quality\n",
         todo["id"]),
        ("[AXIMO] Model Routing Layer v0 (Local-first)",
         "- Local default\n- Claude/GPT fallback\n- Cost/usage guardrails\n- Deterministic logging of provider/model\n",
         todo["id"]),
        ("[AXIMO] Memory Core v0 – Event Schema Design",
         "- Define Event model (who/what/when/why)\n- Approval state (pending/approved/rejected)\n- Temporal base + minimal graph entities\n",
         todo["id"]),
    ]

    print(f"Team: {team['name']} ({team['key']})")
    print(f"Created epic-like issue: {epic['identifier']} {epic['url']}")
    for (title, desc, state_id) in issues:
        issue = create_issue(team["id"], title, desc, state_id)
        print(f"Created: {issue['identifier']} [{issue['title']}] -> {issue['url']}")

if __name__ == "__main__":
    main()
