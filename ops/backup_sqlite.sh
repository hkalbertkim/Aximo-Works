#!/bin/bash
set -euo pipefail

ROOT_DIR="/Users/albertkim/02_PROJECTS/03_aximo"
DB_PATH="$ROOT_DIR/backend/aximo.db"
BACKUP_DIR="$ROOT_DIR/ops/backups/sqlite"
LOG_FILE="$ROOT_DIR/logs/backup_sqlite.out.log"

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

ts() {
  date '+%Y-%m-%d %H:%M:%S %Z'
}

log() {
  printf '[%s] %s\n' "$(ts)" "$1" >> "$LOG_FILE"
}

if [[ ! -f "$DB_PATH" ]]; then
  log "FAIL db file missing: $DB_PATH"
  exit 1
fi

BACKUP_FILE="$BACKUP_DIR/aximo_$(date '+%Y-%m-%d_%H%M%S').db"

if sqlite3 "$DB_PATH" ".backup $BACKUP_FILE"; then
  integrity="$(sqlite3 "$BACKUP_FILE" 'PRAGMA integrity_check;' | tr -d '\r')"
  if [[ "$integrity" != "ok" ]]; then
    log "FAIL integrity_check backup=$BACKUP_FILE result=$integrity"
    exit 1
  fi

  find "$BACKUP_DIR" -type f -name 'aximo_*.db' -mtime +14 -delete
  log "SUCCESS backup=$BACKUP_FILE integrity=ok retention=14d"
else
  log "FAIL sqlite backup command failed db=$DB_PATH"
  exit 1
fi
