#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
P=/home/gee/kiwi-rebase/patches
cd "$S" || exit 1

git diff HEAD --name-only > /tmp/vg_changed.txt
git ls-files --others --exclude-standard >> /tmp/vg_changed.txt

fehlt=0
while read -r p; do
  [ -z "$p" ] && continue
  echo "=== $p"
  grep "^+++ b/" "$P/$p" | sed 's|^+++ b/||' | sort -u > /tmp/vg_files.txt
  while read -r f; do
    [ -z "$f" ] && continue
    if grep -qxF "$f" /tmp/vg_changed.txt; then
      echo "  ok     $f"
    else
      echo "  FEHLT  $f"
      fehlt=$((fehlt+1))
    fi
  done < /tmp/vg_files.txt
done < "$P/series"

echo
echo "fehlende Dateien insgesamt: $fehlt"