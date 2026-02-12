#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dotenv_path = repo_root / ".env"
    if not dotenv_path.exists():
        print("Missing .env. Create .env with LINEAR_API_KEY and LINEAR_TEAM_KEY.", file=sys.stderr)
        return 1

    brief = "\n".join(
        [
            "Daily Brief Update:",
            "- Local LLM validated on M1 Max via Ollama",
            "- llm_local_test.py produced correct code output",
            "- OLLAMA_MODELS pinned to /Volumes/KRAKO_1/ollama_models",
            "- Engine issues created: HKA-71~75",
            "- GitHub repo normalized to main branch",
        ]
    )

    post_cmd = [
        "python3",
        str(repo_root / "scripts" / "post_daily_brief_to_linear.py"),
        "--issue",
        "HKA-38",
        "--text",
        brief,
    ]
    post_result = run_cmd(post_cmd)
    if post_result.returncode != 0:
        if post_result.stderr:
            print(post_result.stderr.strip(), file=sys.stderr)
        else:
            print("Failed to post Daily Brief.", file=sys.stderr)
        return 1

    set_state_cmd = [
        "python3",
        str(repo_root / "scripts" / "set_linear_issue_state.py"),
        "--issue",
        "HKA-73",
        "--state",
        "Done",
    ]
    state_result = run_cmd(set_state_cmd)
    if state_result.returncode != 0:
        combined = "\n".join([state_result.stdout.strip(), state_result.stderr.strip()]).strip()
        if "Issue not found" in combined:
            print("OK: posted Daily Brief to HKA-38. HKA-73 not found, skipped state update.")
            return 0
        if combined:
            print(combined, file=sys.stderr)
        else:
            print("Failed to set issue state for HKA-73.", file=sys.stderr)
        return 1

    print("SUCCESS: posted Daily Brief to HKA-38 and set HKA-73 to Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
