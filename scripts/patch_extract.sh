#!/usr/bin/env bash
cd /home/gee/kiwi-rebase/upstream/src.next
ANCHOR=b2a61e552c94
DEST=/home/gee/kiwi-rebase/patches/by-file
rm -rf "$DEST"; mkdir -p "$DEST"

git -c core.quotePath=false diff --name-only $ANCHOR..kiwi | while IFS= read -r f; do
  safe="$(printf '%s' "$f" | tr '/' '__')"
  git diff --binary $ANCHOR..kiwi -- "$f" > "$DEST/$safe.patch"
done
ls "$DEST" | wc -l          # erwartet: 577