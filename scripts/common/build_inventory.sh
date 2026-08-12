#!/usr/bin/env bash
# build_inventory.sh <ziel-tag>
set -uo pipefail
TAG="${1:?Ziel-Tag angeben, z.B. 149.0.7827.90}"
UP=/home/gee/kiwi-rebase/upstream
REP=/home/gee/kiwi-rebase/reports
SRC=$UP/src.next
ANCHOR=b2a61e552c94

if [ ! -d "$UP/chromium-target-tree" ]; then
  echo ">> Treeless-Clone des Ziels (dauert ein paar Minuten)"
  git clone --filter=blob:none --depth 1 --no-checkout --branch "$TAG" https://chromium.googlesource.com/chromium/src "$UP/chromium-target-tree" || exit 1
fi

cd "$UP/chromium-target-tree"
git -c core.quotePath=false ls-tree -r --name-only HEAD | LC_ALL=C sort > "$REP/upstream-target-paths.txt"
git ls-tree -r HEAD | awk '$2=="commit"{print $4}' | LC_ALL=C sort > "$REP/target-submodules.txt"

cd "$SRC"
git -c core.quotePath=false diff --diff-filter=M --name-only $ANCHOR..kiwi | LC_ALL=C sort > "$REP/kiwi-modified.txt"
git -c core.quotePath=false diff --diff-filter=A --name-only $ANCHOR..kiwi | LC_ALL=C sort > "$REP/kiwi-added.txt"

cd "$REP"
LC_ALL=C comm -12 kiwi-modified.txt upstream-target-paths.txt > risk-a-path-exists.txt
LC_ALL=C comm -23 kiwi-modified.txt upstream-target-paths.txt > risk-b-path-gone.txt

awk -F/ '{print $NF}' upstream-target-paths.txt | LC_ALL=C sort -u > target-basenames.txt
: > risk-b-classified.txt
while IFS= read -r p; do
  b="${p##*/}"
  if LC_ALL=C grep -qxF "$b" target-basenames.txt; then
    echo "MOVED  $p" >> risk-b-classified.txt
  else
    echo "GONE   $p" >> risk-b-classified.txt
  fi
done < risk-b-path-gone.txt

echo
echo "=== Ergebnis fuer $TAG ==="
echo "Kiwi-Eigencode (A), versionsunabhaengig : $(wc -l < kiwi-added.txt)"
echo "Eingriffe (M) gesamt                    : $(wc -l < kiwi-modified.txt)"
echo "  A  Pfad existiert im Ziel             : $(wc -l < risk-a-path-exists.txt)"
echo "  B  Pfad weg                           : $(wc -l < risk-b-path-gone.txt)"
awk '{print "     "$1}' risk-b-classified.txt | sort | uniq -c
echo
echo "=== Eingriffe nach Subsystem ==="
awk -F/ '{if(NF>=3) print $1"/"$2"/"$3; else print $0}' kiwi-modified.txt | sort | uniq -c | sort -rn | head -15