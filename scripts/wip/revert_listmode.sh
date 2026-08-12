#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1
T=chrome/android/features/tab_ui

git checkout HEAD -- $T/BUILD.gn
git checkout HEAD -- $T/tab_management_java_sources.gni
git checkout HEAD -- $T/java/res/values/dimens.xml
git checkout HEAD -- $T/java/src/org/chromium/chrome/browser/tasks/tab_management/

rm -f $T/java/res/layout/tab_list_card_item.xml
rm -f $T/java/res/drawable/selected_tab_background.xml
rm -f $T/java/res/drawable/selected_tab_background_incognito.xml
rm -f $T/java/src/org/chromium/chrome/browser/tasks/tab_management/TabListView.java
rm -f $T/java/src/org/chromium/chrome/browser/tasks/tab_management/TabListViewBinder.java

echo "=== verbleibende Aenderungen ==="
git status --short