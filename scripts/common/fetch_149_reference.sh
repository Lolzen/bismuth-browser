#!/usr/bin/env bash
TREE=/home/gee/kiwi-rebase/upstream/chromium-target-tree
OUT=/home/gee/kiwi-rebase/reports/149-reference
mkdir -p "$OUT"
cd "$TREE" || exit 1

B=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management
for f in \
  "$B/TabUiFeatureUtilities.java" \
  "$B/TabListCoordinator.java" \
  "$B/TabSwitcherPaneCoordinatorFactory.java" \
  "$B/TabSwitcherPaneBase.java" \
  "$B/TabListContainerProperties.java" \
; do
  n="${f##*/}"
  if git show "HEAD:$f" > "$OUT/$n" 2>/dev/null; then
    echo "ok   $n  ($(wc -l < "$OUT/$n") Zeilen)"
  else
    echo "FEHL $n"
  fi
done

echo
echo "=== Modus-relevante Stellen ==="
grep -n 'TabListMode\|ListMode\|shouldUseListMode\|GRID\|LIST' "$OUT/TabUiFeatureUtilities.java" "$OUT/TabSwitcherPaneCoordinatorFactory.java" 2>/dev/null | head -40