#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== chrome_build.gni 30-70 ==="
sed -n '30,70p' build/config/chrome_build.gni

echo
echo "=== chrome/android/BUILD.gn ==="
git grep -n -B3 -A6 "is_desktop_android" -- chrome/android/BUILD.gn

echo
echo "=== chrome/version.gni ==="
git grep -n -B3 -A6 "is_desktop_android" -- chrome/version.gni

echo
echo "=== chrome/chrome_paks.gni ==="
git grep -n -B2 -A6 "is_desktop_android" -- chrome/chrome_paks.gni

echo
echo "=== rules.gni 2035-2055 ==="
sed -n '2035,2055p' build/config/android/rules.gni