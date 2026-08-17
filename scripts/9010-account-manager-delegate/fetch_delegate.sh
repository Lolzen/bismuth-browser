#!/usr/bin/env bash
T=/home/gee/kiwi-rebase/upstream/chromium-132-tree
OUT=/home/gee/kiwi-rebase/reports/signin-reference-132
mkdir -p "$OUT"
cd "$T" || exit 1
B=components/signin/public/android/java/src/org/chromium/components/signin
for f in SystemAccountManagerDelegate.java AccountManagerDelegate.java AccessTokenData.java AuthException.java AccountsChangeObserver.java; do
  if git show "HEAD:$B/$f" > "$OUT/$f" 2>/dev/null; then
    echo "ok   $f  ($(wc -l < "$OUT/$f") Zeilen)"
  else
    echo "FEHL $f"
  fi
done