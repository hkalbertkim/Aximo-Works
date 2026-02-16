# SQLite Backup Runbook

## Manual backup
Run from anywhere:

```bash
/bin/bash /Users/albertkim/02_PROJECTS/03_aximo/ops/backup_sqlite.sh
```

## Load/unload launchd job
Load (or reload) the job:

```bash
launchctl bootout gui/$(id -u)/com.aximo.backup_sqlite 2>/dev/null || true
launchctl bootstrap gui/$(id -u) /Users/albertkim/02_PROJECTS/03_aximo/ops/launchd/com.aximo.backup_sqlite.plist
```

Unload the job:

```bash
launchctl bootout gui/$(id -u)/com.aximo.backup_sqlite
```

Run immediately for test:

```bash
launchctl kickstart -k gui/$(id -u)/com.aximo.backup_sqlite
```

## Verify backups
List latest backup files:

```bash
ls -la /Users/albertkim/02_PROJECTS/03_aximo/ops/backups/sqlite | tail -n 10
```

Check integrity of a backup:

```bash
sqlite3 /Users/albertkim/02_PROJECTS/03_aximo/ops/backups/sqlite/<backup_file>.db "PRAGMA integrity_check;"
```

## Log locations
- Backup script log: `/Users/albertkim/02_PROJECTS/03_aximo/logs/backup_sqlite.out.log`
- launchd stdout/stderr: `/Users/albertkim/02_PROJECTS/03_aximo/logs/backup_sqlite.launchd.log`
