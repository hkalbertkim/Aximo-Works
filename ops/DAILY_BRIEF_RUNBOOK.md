# Daily Brief Runbook

## Purpose
Generate a daily operational summary from SQLite tasks and send it to Telegram.
Also posts to Linear HKA-38 when LINEAR_* env vars are present.

## Manual run
```bash
/Users/albertkim/miniconda3/bin/python /Users/albertkim/02_PROJECTS/03_aximo/ops/daily_brief.py
```

## launchd load/unload
Load or reload:
```bash
launchctl bootout gui/$(id -u)/com.aximo.daily_brief 2>/dev/null || true
launchctl bootstrap gui/$(id -u) /Users/albertkim/02_PROJECTS/03_aximo/ops/launchd/com.aximo.daily_brief.plist
```

Unload:
```bash
launchctl bootout gui/$(id -u)/com.aximo.daily_brief
```

Kickstart test run:
```bash
launchctl kickstart -k gui/$(id -u)/com.aximo.daily_brief
```

## Data + log paths
- SQLite DB: `/Users/albertkim/02_PROJECTS/03_aximo/backend/aximo.db`
- Script log: `/Users/albertkim/02_PROJECTS/03_aximo/logs/daily_brief.out.log`
- launchd log: `/Users/albertkim/02_PROJECTS/03_aximo/logs/daily_brief.launchd.log`
