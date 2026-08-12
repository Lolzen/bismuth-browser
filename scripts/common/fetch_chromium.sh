#!/usr/bin/env bash
set -e
B=/home/gee/kiwi-rebase/build
TAG=149.0.7827.238
export PATH="$B/depot_tools:$PATH"
export TMPDIR="$B/tmp"
mkdir -p "$TMPDIR"

[ -d "$B/depot_tools" ] || git clone \
  https://chromium.googlesource.com/chromium/tools/depot_tools.git "$B/depot_tools"

mkdir -p "$B/chromium"
cd "$B/chromium"

cat > .gclient <<GCLIENT
solutions = [
  {
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git@$TAG",
    "managed": True,
    "custom_deps": {},
    "custom_vars": {},
  },
]
target_os = ["android"]
GCLIENT

gclient sync --with_branch_heads --with_tags -D