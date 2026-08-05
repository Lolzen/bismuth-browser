#!/usr/bin/env bash
REP=/home/gee/kiwi-rebase/reports
B=chrome/android/features/tab_ui/java
for f in \
  "$B/src/org/chromium/chrome/browser/tasks/tab_management/TabListViewBinder.java" \
  "$B/src/org/chromium/chrome/browser/tasks/tab_management/TabProperties.java" \
  "$B/res/layout/tab_list_card_item.xml" \
; do
  if grep -qxF "$f" "$REP/upstream-target-paths.txt"; then
    echo "IN 149   ${f##*/}"
  else
    echo "FEHLT    ${f##*/}"
  fi
done
echo
echo "=== Verwandte Layouts in 149 ==="
grep 'tab_ui/java/res/layout/' "$REP/upstream-target-paths.txt" | grep -i 'list\|card\|item'