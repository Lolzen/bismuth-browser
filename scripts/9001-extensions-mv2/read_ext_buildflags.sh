#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== buildflags.gni ==="
cat extensions/buildflags/buildflags.gni

echo
echo "=== wo enable_desktop_android_extensions greift ==="
git grep -ln "enable_desktop_android_extensions" | head -30

echo
echo "=== ENABLE_DESKTOP_ANDROID_EXTENSIONS im Code ==="
git grep -ln "ENABLE_DESKTOP_ANDROID_EXTENSIONS" | head -30