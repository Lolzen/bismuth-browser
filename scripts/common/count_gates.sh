#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== Vorkommen mit is_desktop_android ==="
git grep -c "is_desktop_android" -- "*.gn" "*.gni" | sort -t: -k2 -rn | head -20

echo
echo "=== Gesamtzahl der Zeilen ==="
git grep -h "is_desktop_android" -- "*.gn" "*.gni" | wc -l

echo
echo "=== was is_desktop_android sonst noch bewirkt ==="
git grep -rn "is_desktop_android" -- build/config/ | head -20