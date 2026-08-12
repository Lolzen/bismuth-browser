#!/usr/bin/env bash
set -e
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
S=/home/gee/kiwi-rebase/build/chromium/src

rm -rf "$S/third_party/dawn"

cd /home/gee/kiwi-rebase/build/chromium
gclient sync --force --reset --with_branch_heads --with_tags -D