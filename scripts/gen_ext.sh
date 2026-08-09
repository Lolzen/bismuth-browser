#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
cd "$S"

mkdir -p out/Ext
cp out/Vanilla/args.gn out/Ext/args.gn
echo 'enable_desktop_android_extensions = true' >> out/Ext/args.gn

gn gen out/Ext
gn args out/Ext --list --short | grep -i "enable_extensions\|desktop_android"