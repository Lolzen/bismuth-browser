#!/usr/bin/env bash
P=/home/gee/kiwi-rebase/patches
cd "$P" || exit 1

mkdir -p archive reference

# LIST-Sackgasse aufheben, aber aus der Serie nehmen
[ -f 9002-tabswitcher-list-archiv.patch ] && mv 9002-tabswitcher-list-archiv.patch archive/

# ueberholte kumulative Fassungen
for f in 9001-android-extensions-mv2.patch 9001-android-extensions.patch \
         9001-mv2-enabled.patch 9002-tabswitcher-list-wip.patch \
         9004-webstore-desktop-exception.patch; do
  [ -f "$f" ] && rm -v "$f"
done

# Kiwis extrahierte Patches sind Referenz, nicht Teil der Serie
for d in by-commit by-file; do
  [ -d "$d" ] && mv "$d" reference/ && echo "-> reference/$d"
done

echo
echo "=== Serie ==="
n=0
while read -r p; do
  [ -z "$p" ] && continue
  if [ -f "$p" ]; then
    c=$(grep -c '^diff --git' "$p")
    n=$((n+c))
    printf '  %-40s %2d Dateien\n' "$p" "$c"
  else
    echo "  FEHLT: $p"
  fi
done < series
echo "  Summe: $n (erwartet 31)"

echo
echo "=== uebrig ==="
ls -p | grep -v /