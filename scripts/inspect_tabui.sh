#!/usr/bin/env bash
SRC=/home/gee/kiwi-rebase/upstream/src.next
ANCHOR=b2a61e552c94
cd "$SRC" || exit 1

echo "=== Commits, die Tab-Switcher-Code anfassen ==="
git log --oneline $ANCHOR..kiwi -- 'chrome/android/features/tab_ui/*' '*TabSwitcher*' '*PseudoTab*'

echo
echo "=== Umfang pro Datei ==="
git diff --stat $ANCHOR..kiwi -- 'chrome/android/features/tab_ui/*' '*TabSwitcher*' '*PseudoTab*'

echo
echo "=== Kiwis eigener Einstellungsschirm ==="
git show kiwi:chrome/android/java/src/org/chromium/chrome/browser/settings/TabSwitcherSettings.java 2>/dev/null | head -80

echo
echo "=== Die eigentlichen Aenderungen an TabSwitcherMediator ==="
git diff $ANCHOR..kiwi -- 'chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/TabSwitcherMediator.java'