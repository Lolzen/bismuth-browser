#!/usr/bin/env bash
set -e
NAME="${1:?Kurzname angeben, z.B. copyload}"
R=/home/gee/kiwi-rebase
S=$R/build/chromium/src
OUT=$R/artifacts
STAMP=$(date +%Y%m%d-%H%M)

mkdir -p "$OUT"
cp "$S/out/Ext/apks/ChromePublic.apk" "$OUT/$STAMP-$NAME.apk"
cp "$S/out/Ext/args.gn" "$OUT/$STAMP-$NAME.args.gn"
cd "$S"
git diff HEAD > "$OUT/$STAMP-$NAME.patch"

ls -lh "$OUT" | tail -6