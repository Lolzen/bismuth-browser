#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== mdns/BUILD.gn ==="
sed -n '1,35p' chrome/browser/extensions/api/mdns/BUILD.gn

echo
echo "=== enable_media_router als declare_arg ==="
git grep -n "enable_media_router" -- "*.gni" | head

echo
echo "=== wer haengt an mdns ==="
git grep -n "api/mdns" -- "*.gn" "*.gni" | head