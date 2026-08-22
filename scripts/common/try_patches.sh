#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
P=/home/gee/kiwi-rebase/patches
cd "$S" || exit 1
ok=0; fail=0
while read -r p; do
  [ -z "$p" ] && continue
  if git apply --3way --check "$P/$p" 2>/dev/null; then
    echo "OK    $p"
    ok=$((ok+1))
  else
    n=$(git apply --3way --check "$P/$p" 2>&1 | grep -c "error")
    echo "FEHL  $p  ($n Meldungen)"
    fail=$((fail+1))
  fi
done < "$P/series"
echo
echo "sauber: $ok   mit Konflikt: $fail"