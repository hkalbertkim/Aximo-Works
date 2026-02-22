import json
import os
import urllib.error
import urllib.request


def send_telegram(text: str, chat_id: str | int | None = None, reply_markup: dict | None = None) -> int | None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    target_chat_id = str(chat_id).strip() if chat_id is not None else os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not target_chat_id:
        print("TELEGRAM notify skipped: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict = {"chat_id": target_chat_id, "text": text}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            if status != 200:
                body = resp.read().decode("utf-8", errors="replace")
                print(f"TELEGRAM notify failed: status={status} body={body[:200]}")
            return status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"TELEGRAM notify failed: status={e.code} body={body[:200]}")
        return int(e.code)
    except Exception as e:
        print(f"TELEGRAM notify failed: {repr(e)}")
        return None
