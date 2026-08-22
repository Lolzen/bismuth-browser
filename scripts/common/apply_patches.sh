#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
P=/home/gee/kiwi-rebase/patches
cd "$S" || exit 1
while read -r p; do
  [ -z "$p" ] && continue
  if git apply --3way "$P/$p" 2>/dev/null; then
    echo "OK    $p"
  else
    echo "FEHL  $p"
  fi
done < "$P/series"
echo
git diff --stat | tail -1