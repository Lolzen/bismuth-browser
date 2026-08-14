#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
OUT=/home/gee/kiwi-rebase/patches
TAG=$(cat /home/gee/kiwi-rebase/CHROMIUM_TARGET)
cd "$S"
git add -A

mk() {
  n="$1"; shift
  git diff --binary --cached "$TAG" -- "$@" > "$OUT/$n.patch"
  echo "$n.patch  $(grep -c '^diff --git' "$OUT/$n.patch") Dateien"
}

mk 9001-extensions-mv2 \
  base/files/file_enumerator_posix.cc \
  extensions/common/extension_features.cc \
  chrome/common/extensions/api/api_sources.gni

mk 9002-classic-tabswitcher \
  chrome/android/features/tab_ui

mk 9003-extension-copy-on-load \
  chrome/browser/extensions/api/developer_private/developer_private_functions.cc \
  chrome/browser/extensions/api/developer_private/developer_private_functions.h

mk 9004-webstore-desktop \
  chrome/android/java/src/org/chromium/chrome/browser/ui/RootUiCoordinator.java \
  chrome/browser/ui/android/desktop_site

mk 9005-branding \
  chrome/android/chrome_public_apk_tmpl.gni \
  chrome/android/java/res_base/drawable \
  chrome/android/java/res_chromium_base

mk 9006-extensions-menu \
  chrome/android/java/src/org/chromium/chrome/browser/ChromeTabbedActivity.java \
  chrome/android/java/src/org/chromium/chrome/browser/tabbed_mode/TabbedAppMenuPropertiesDelegate.java \
  chrome/browser/flags/android/chrome_feature_list.cc

mk 9007-mv2-no-deprecation \
  extensions/common/extension.cc \
  chrome/browser/extensions/api/developer_private/extension_info_generator.cc

git reset -q

cat > "$OUT/series" <<SERIES
9001-extensions-mv2.patch
9002-classic-tabswitcher.patch
9003-extension-copy-on-load.patch
9004-webstore-desktop.patch
9005-branding.patch
9006-extensions-menu.patch
9007-mv2-no-deprecation.patch
SERIES
echo
echo "series geschrieben"