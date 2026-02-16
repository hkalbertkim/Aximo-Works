# AXIMO Ops Quickcheck

Run from: `/Users/albertkim/02_PROJECTS/03_aximo`

## 1) Local checks
```bash
curl -I -s http://127.0.0.1:3000 | head -n 1
# expected: HTTP/1.1 200 OK

curl -s http://127.0.0.1:8000/health
# expected JSON: {"ok": true, ... , "service":"aximo-backend"}
```

## 2) Cloudflare Access checks
```bash
curl -I -s https://meeting.aximo.works | sed -n '1,5p'
# expected: HTTP/2 302 + Location: https://aximo.cloudflareaccess.com/...

curl -I -s https://api.aximo.works/tasks | sed -n '1,5p'
# expected: HTTP/2 302 + Location: https://aximo.cloudflareaccess.com/...
```

## 3) SQLite backup checks
```bash
ls -lt /Users/albertkim/02_PROJECTS/03_aximo/ops/backups/sqlite | head -n 5
# expected: recent aximo_YYYY-MM-DD_HHMMSS.db files

tail -n 20 /Users/albertkim/02_PROJECTS/03_aximo/logs/backup_sqlite.out.log
# expected: SUCCESS ... integrity=ok retention=14d
```

## 4) Daily brief checks
```bash
tail -n 20 /Users/albertkim/02_PROJECTS/03_aximo/logs/daily_brief.out.log
# expected: SUCCESS daily brief sent or SKIP already sent today

cat /Users/albertkim/02_PROJECTS/03_aximo/ops/state/daily_brief_last_sent.txt
# state file path above; expected YYYY-MM-DD
```

## 5) launchd status (all 5 labels)
```bash
uid=$(id -u)
for label in \
  com.aximo.frontend \
  com.aximo.backend \
  com.aximo.cloudflared \
  com.aximo.backup_sqlite \
  com.aximo.daily_brief; do
  echo "== $label =="
  launchctl print gui/${uid}/${label} 2>/dev/null | awk '/state =|pid =|last exit code =|active count =/ {print}'
done
```
