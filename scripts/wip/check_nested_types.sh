#!/usr/bin/env bash
REP=/home/gee/kiwi-rebase/reports
REF=$REP/list-reference-138.0.7204.310
NEW=$REP/149-reference

echo "=== verschachtelte Typen, die der 138er Binder nutzt ==="
grep -o 'TabProperties\.[A-Z][A-Za-z0-9_]*' "$REF/TabListViewBinder.java" | sed 's/TabProperties\.//' | grep -v '^[A-Z_]*$' | sort -u > /tmp/nested.txt
cat /tmp/nested.txt

echo
echo "=== in 149 vorhanden? ==="
while IFS= read -r t; do
  grep -q "\b$t\b" "$NEW/TabProperties.java" && echo "ok      $t" || echo "FEHLT   $t"
done < /tmp/nested.txt

echo
echo "=== UiType-Werte im Vergleich ==="
echo "--- 138 ---"; grep -A20 'interface UiType\|@interface UiType' "$REF/TabProperties.java" | grep 'int '
echo "--- 149 ---"; grep -A20 'interface UiType\|@interface UiType' "$NEW/TabProperties.java" | grep 'int '