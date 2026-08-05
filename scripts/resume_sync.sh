#!/usr/bin/env bash
B=/home/gee/kiwi-rebase/build
export PATH="$B/depot_tools:$PATH"
export TMPDIR="$B/tmp"
cd "$B/chromium" || exit 1

for i in 1 2 3 4 5 6; do
  echo "=== Versuch $i ==="
  if gclient sync --jobs 4 --with_branch_heads --with_tags -D; then
    echo "=== Sync erfolgreich ==="
    exit 0
  fi
  echo "=== fehlgeschlagen, warte 10 Minuten ==="
  sleep 600
done
echo "=== nach 6 Versuchen immer noch nicht durch ==="
exit 1