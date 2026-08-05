#!/usr/bin/env bash
# fetch_list_reference.sh <tag-mit-LIST>
T="${1:?Tag angeben, z.B. 139.0.7258.xxx}"
R=https://chromium.googlesource.com/chromium/src
OUT=/home/gee/kiwi-rebase/reports/list-reference-$T
B=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management
mkdir -p "$OUT"

for f in \
  "$B/TabListCoordinator.java" \
  "$B/TabListMediator.java" \
  "$B/TabListContainerViewBinder.java" \
  "$B/TabListViewBinder.java" \
  "$B/TabProperties.java" \
  "$B/TabSwitcherPaneCoordinatorFactory.java" \
  chrome/android/features/tab_ui/java/res/layout/tab_list_card_item.xml ; do
  n="${f##*/}"
  if curl -sf "$R/+/refs/tags/$T/$f?format=TEXT" -o /tmp/x.b64; then
    base64 -d < /tmp/x.b64 > "$OUT/$n"
    echo "ok   $n  ($(wc -l < "$OUT/$n") Zeilen)"
  else
    echo "FEHL $n"
  fi
  sleep 0.2
done

echo
echo "=== LIST-Stellen in der Referenz ==="
grep -n 'TabListMode.LIST\|LinearLayoutManager\|VERTICAL' "$OUT"/*.java | head -30