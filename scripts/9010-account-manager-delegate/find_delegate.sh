#!/usr/bin/env bash
for t in chromium-target-tree chromium-132-tree src.next; do
  echo "=== $t ==="
  cd "/home/gee/kiwi-rebase/upstream/$t" 2>/dev/null || { echo "fehlt"; continue; }
  git ls-tree -r --name-only HEAD 2>/dev/null | grep -i "accountmanagerdelegate" | head -10
  echo
done