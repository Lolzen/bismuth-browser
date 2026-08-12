#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== wo liegt modern_list_item_view.xml ==="
find . -name "modern_list_item_view.xml" -not -path "./out/*"

echo
echo "=== enthaelt es die beiden IDs? ==="
grep -rn "after_title_container\|before_description_container" --include=*.xml components/ chrome/ | head -5

echo
echo "=== TabCardThemeUtil ==="
F=$(find . -name TabCardThemeUtil.java -not -path "./out/*" | head -1)
echo "$F"
grep -n "public static" "$F"

echo
echo "=== wie ruft TabGridViewBinder auf ==="
sed -n '300,312p' chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/TabGridViewBinder.java