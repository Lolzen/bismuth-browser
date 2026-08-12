#!/usr/bin/env bash
SRC=/home/gee/kiwi-rebase/upstream/src.next
REP=/home/gee/kiwi-rebase/reports
ANCHOR=b2a61e552c94
cd "$SRC" || exit 1

git diff --name-only $ANCHOR..kiwi -- 'chrome/android/features/tab_ui/*' '*TabSwitcher*' '*PseudoTab*' | LC_ALL=C sort > /tmp/tabui-files.txt

echo "=== existiert in 149 ==="
LC_ALL=C comm -12 /tmp/tabui-files.txt "$REP/upstream-target-paths.txt"
echo
echo "=== nicht mehr vorhanden ==="
LC_ALL=C comm -23 /tmp/tabui-files.txt "$REP/upstream-target-paths.txt"
echo
echo "=== Kandidaten im Ziel mit aehnlichem Namen ==="
LC_ALL=C comm -23 /tmp/tabui-files.txt "$REP/upstream-target-paths.txt" | sed 's|.*/||; s|\.java$||' | grep -f - "$REP/upstream-target-paths.txt" | head -30

echo
echo "=== was 149 im tab_ui-Bereich ueberhaupt hat ==="
grep 'tab_management\|tab_ui' "$REP/upstream-target-paths.txt" | grep -i 'switcher\|tablist' | head -30