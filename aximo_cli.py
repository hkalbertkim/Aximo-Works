#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timezone

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


COMMANDS = {"today", "decided", "risk"}

RESPONSES = {
    "today": (
        "*TODAY - Top actions*",
        [
            "- [placeholder] Review urgent Slack threads and pick top 3.",
            "- [placeholder] Confirm owner + deadline for each open blocker.",
            "- [placeholder] Schedule one 15-minute risk check-in.",
        ],
    ),
    "decided": (
        "*DECIDED - Recent calls*",
        [
            "- [placeholder] Keep Slack as primary ops command channel.",
            "- [placeholder] Limit ingestion to Gmail read-only for v0.1.",
            "- [placeholder] Ship daily brief once/day, no external sending.",
        ],
    ),
    "risk": (
        "*RISK - Next issues*",
        [
            "- [placeholder] Missing owner on high-priority action items.",
            "- [placeholder] Delayed replies could hide urgent dependencies.",
            "- [placeholder] Scope creep beyond 3 core questions.",
        ],
    ),
}


def print_usage() -> None:
    print("Usage: python3 aximo_cli.py [today|decided|risk]")


def build_message(command: str) -> str:
    header, bullets = RESPONSES[command]
    return "\n".join([header, *bullets])


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print_usage()
        return 1

    command = sys.argv[1]
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("Error: SLACK_BOT_TOKEN is required.")
        return 1

    channel = os.getenv("SLACK_CHANNEL", "#new-channel")
    client = WebClient(token=token)
    message = build_message(command)

    try:
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as exc:
        err = exc.response.get("error", "unknown_error")
        print(f"Slack API error: {err}")
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return 1

    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"Posted {command} to Slack at {timestamp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
