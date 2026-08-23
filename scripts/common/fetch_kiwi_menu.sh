#!/usr/bin/env bash
T=/home/gee/kiwi-rebase/upstream/src.next
OUT=/home/gee/kiwi-rebase/reports/kiwi-extension-menu
BASE=b2a61e552c94
mkdir -p "$OUT"
cd "$T" || exit 1

A=chrome/android/java/src/org/chromium/chrome/browser/app/appmenu
B=chrome/browser/ui/android/appmenu/internal/java/src/org/chromium/chrome/browser/ui/appmenu

for f in \
  "$A/AppMenuPropertiesDelegateImpl.java" \
  "$B/AppMenu.java" \
  "$B/AppMenuAdapter.java" \
  "$B/AppMenuHandlerImpl.java" \
  "$B/AppMenuItemViewBinder.java" \
  "chrome/android/java/res/menu/main_menu.xml" \
; do
  n="${f##*/}"
  git diff "$BASE" HEAD -- "$f" > "$OUT/$n.diff" 2>/dev/null
  z=$(wc -l < "$OUT/$n.diff")
  e=$(grep -ci "extension" "$OUT/$n.diff")
  echo "$n  $z Zeilen Diff, $e mit Extension-Bezug"
done
echo
echo "Diffs in $OUT"