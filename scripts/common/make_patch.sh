#!/usr/bin/env bash
set -e
N="${1:?Nummer}"
NAME="${2:?Kurzname}"
R=/home/gee/kiwi-rebase
S=$R/build/chromium/src
TAG=149.0.7827.238
OUT="$R/patches"
mkdir -p "$OUT"

cd "$S"
git add -A
git diff --binary --cached "$TAG" > "$OUT/$N-$NAME.patch"
git reset -q
grep -q "$N-$NAME.patch" "$OUT/series" 2>/dev/null || echo "$N-$NAME.patch" >> "$OUT/series"
wc -l "$OUT/$N-$NAME.patch"