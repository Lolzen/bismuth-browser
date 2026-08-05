#!/usr/bin/env bash
TREE=/home/gee/kiwi-rebase/upstream/chromium-target-tree
REP=/home/gee/kiwi-rebase/reports
REF=$REP/list-reference-138.0.7204.310
OUT=$REP/149-reference
P=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/TabProperties.java
mkdir -p "$OUT"

git -C "$TREE" show "HEAD:$P" > "$OUT/TabProperties.java" || exit 1
echo "138: $(wc -l < "$REF/TabProperties.java") Zeilen"
echo "149: $(wc -l < "$OUT/TabProperties.java") Zeilen"

echo
echo "=== Diff 138 -> 149 ==="
diff -u "$REF/TabProperties.java" "$OUT/TabProperties.java" > "$REP/tabproperties-138-vs-149.diff"
echo "entfernt: $(grep -c '^-[^-]' "$REP/tabproperties-138-vs-149.diff")"
echo "neu:      $(grep -c '^+[^+]' "$REP/tabproperties-138-vs-149.diff")"
echo "-> $REP/tabproperties-138-vs-149.diff"

echo
echo "=== entfernte PropertyKeys ==="
grep '^-.*PropertyKey\|^-.*WritableObjectPropertyKey\|^-.*WritableIntPropertyKey\|^-.*ReadableObjectPropertyKey\|^-.*WritableBooleanPropertyKey' "$REP/tabproperties-138-vs-149.diff" | sed 's/^-//' | head -30

echo
echo "=== Keys, die TabListViewBinder (138) braucht, in 149 pruefen ==="
grep -o 'TabProperties\.[A-Z_][A-Z0-9_]*' "$REF/TabListViewBinder.java" | sed 's/TabProperties\.//' | sort -u > /tmp/needed-keys.txt
echo "benoetigte Keys: $(wc -l < /tmp/needed-keys.txt)"
while IFS= read -r k; do
  grep -q "\b$k\b" "$OUT/TabProperties.java" && echo "ok      $k" || echo "FEHLT   $k"
done < /tmp/needed-keys.txt