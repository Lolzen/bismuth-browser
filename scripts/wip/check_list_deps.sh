#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
T=$S/chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management
R=/home/gee/kiwi-rebase/reports/list-reference-138.0.7204.310
TAG=138.0.7204.310
BASE=https://chromium.googlesource.com/chromium/src/+/refs/tags/$TAG

echo "=== View-Klassen in 149 ==="
ls "$T" | grep -iE "TabListView|TabGridView|TabStripView"

echo
echo "=== Chromium-Importe des 138er Binders ==="
grep -n "^import org.chromium" "$R/TabListViewBinder.java"

echo
echo "=== fehlt davon etwas in 149? ==="
grep "^import org.chromium" "$R/TabListViewBinder.java" \
  | sed 's/^import //; s/;$//' | while read -r c; do
      p=$(echo "$c" | tr '.' '/')
      if [ -z "$(find "$S" -path "*/$p.java" -print -quit 2>/dev/null)" ]; then
        echo "FEHLT   $c"
      fi
    done

echo
echo "=== Layout aus 138 holen ==="
L=chrome/android/features/tab_ui/java/res/layout/tab_list_card_item.xml
if curl -sf "$BASE/$L?format=TEXT" -o /tmp/l.b64; then
  base64 -d < /tmp/l.b64 > "$R/tab_list_card_item.xml"
  echo "ok  $(wc -l < "$R/tab_list_card_item.xml") Zeilen"
else
  echo "FEHLGESCHLAGEN"
fi