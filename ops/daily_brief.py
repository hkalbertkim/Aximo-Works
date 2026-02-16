#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sqlite3
import sys
import json
import urllib.request
import urllib.error

ROOT = Path('/Users/albertkim/02_PROJECTS/03_aximo')
DB_PATH = ROOT / 'backend' / 'aximo.db'
BACKEND_ENV = ROOT / 'backend' / '.env'
LOG_PATH = ROOT / 'logs' / 'daily_brief.out.log'
BACKEND_DIR = ROOT / 'backend'
STATE_DIR = ROOT / 'ops' / 'state'
LAST_SENT_FILE = STATE_DIR / 'daily_brief_last_sent.txt'


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def log_line(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')


def local_date_str() -> str:
    return datetime.now().astimezone().strftime('%Y-%m-%d')


def already_sent_today() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not LAST_SENT_FILE.exists():
        return False
    return LAST_SENT_FILE.read_text(encoding='utf-8').strip() == local_date_str()


def mark_sent_today() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LAST_SENT_FILE.write_text(local_date_str(), encoding='utf-8')


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            os.environ[key] = value


def require_telegram_env() -> tuple[str, str]:
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    missing: list[str] = []
    if not token:
        missing.append('TELEGRAM_BOT_TOKEN')
    if not chat_id:
        missing.append('TELEGRAM_CHAT_ID')
    if missing:
        msg = (
            f"Missing required env var(s): {', '.join(missing)}. "
            'Normally set in /Users/albertkim/02_PROJECTS/03_aximo/backend/.env '
            'and launchd plist com.aximo.backend.'
        )
        log_line(f'FAIL {msg}')
        raise RuntimeError(msg)
    return token, chat_id


def validate_telegram_token(token: str) -> None:
    req = urllib.request.Request(f'https://api.telegram.org/bot{token}/getMe', method='GET')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            payload = json.loads(body)
            if resp.getcode() != 200 or payload.get('ok') is not True:
                raise RuntimeError('Telegram getMe validation failed')
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Telegram getMe failed with HTTP {e.code}') from None
    except Exception as e:
        raise RuntimeError(f'Telegram getMe validation error: {e}') from None


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def build_brief() -> str:
    if not DB_PATH.exists():
        raise RuntimeError(f'SQLite DB not found: {DB_PATH}')

    cutoff = now_utc() - timedelta(hours=24)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        total_tasks = int(conn.execute('SELECT COUNT(*) AS c FROM tasks').fetchone()['c'])

        rows = conn.execute(
            'SELECT id, text, status, created_at, ran_at FROM tasks ORDER BY COALESCE(ran_at, created_at) DESC'
        ).fetchall()

        created_24h = 0
        completed_24h = 0
        for r in rows:
            created_dt = parse_iso(r['created_at'])
            updated_dt = parse_iso(r['ran_at']) or created_dt

            if created_dt and created_dt >= cutoff:
                created_24h += 1
            if r['status'] == 'done' and updated_dt and updated_dt >= cutoff:
                completed_24h += 1

        top_rows = rows[:5]
        lines = [
            'AXIMO Daily Brief',
            f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
            '',
            f'- Total tasks: {total_tasks}',
            f'- Created (last 24h): {created_24h}',
            f'- Completed (last 24h): {completed_24h}',
            '',
            'Top 5 recent tasks:',
        ]

        if not top_rows:
            lines.append('- (no tasks)')
        else:
            for row in top_rows:
                updated_at = row['ran_at'] or row['created_at'] or '-'
                text = (row['text'] or '').replace('\n', ' ').strip()
                if len(text) > 90:
                    text = text[:87] + '...'
                lines.append(f"- {text} | status={row['status']} | updated_at={updated_at}")

        return '\n'.join(lines)
    finally:
        conn.close()


def send_brief_with_existing_sender(message: str) -> None:
    sys.path.insert(0, str(BACKEND_DIR))
    from main import send_telegram  # reuse existing integration

    send_telegram(message)


def main() -> int:
    if already_sent_today():
        log_line('SKIP already sent today')
        print('DAILY_BRIEF_SKIP')
        return 0

    load_env_file(BACKEND_ENV)
    token, _ = require_telegram_env()
    validate_telegram_token(token)

    brief = build_brief()
    send_brief_with_existing_sender(brief)
    mark_sent_today()

    log_line('SUCCESS daily brief sent')
    print('DAILY_BRIEF_OK')
    preview = '\n'.join(brief.splitlines()[:20])
    print(preview)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as e:
        log_line(f'FAIL {e}')
        print(f'DAILY_BRIEF_FAIL: {e}')
        raise SystemExit(1)
