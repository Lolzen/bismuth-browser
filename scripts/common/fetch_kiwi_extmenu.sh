#!/usr/bin/env bash
T=/home/gee/kiwi-rebase/upstream/src.next
OUT=/home/gee/kiwi-rebase/reports/kiwi-extension-menu
mkdir -p "$OUT"
cd "$T" || exit 1
for c in c87978cc1ea2 b31f5ba0d9b5 043d6dd1803b 5dbeb7ff56de; do
  if git show "$c" > "$OUT/$c.diff" 2>/dev/null; then
    echo "=== $c  ($(wc -l < "$OUT/$c.diff") Zeilen)"
    git show --stat --oneline "$c" | head -8
    echo
  else
    echo "FEHL $c"
  fi
done