import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def main():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN not set")

    channel = os.environ.get("SLACK_CHANNEL", "#new-channel")  # 기본: #new-channel
    client = WebClient(token=token)

    try:
        resp = client.chat_postMessage(
            channel=channel,
            text="👋 I’m live. Aximo is working."
        )
        print("Sent message ts:", resp["ts"])
    except SlackApiError as e:
        print("SlackApiError:", e.response["error"])
        raise

if __name__ == "__main__":
    main()
