#!/usr/bin/env bash
set -e
REP=/home/gee/kiwi-rebase/reports
SRC=/home/gee/kiwi-rebase/upstream/src.next
ANCHOR=b2a61e552c94

DROP='\.png$|^\.github|^\.gitignore$|^\.build/|^toolbox/|kiwi_logo|^VERSION$|^KIWI_VERSION$|^CHROMIUM_VERSION$|fetch_from_upstream|^remoting/|signin/ui/|browser/ui/extensions/|StartSurface|NewTabTile|PseudoTab'

cd "$SRC"
git -c core.quotePath=false diff --name-status "$ANCHOR"..kiwi | grep -Ev "$DROP" > "$REP/worklist-full.txt"

awk -F'\t' '$1=="A"{print $2}' "$REP/worklist-full.txt" | LC_ALL=C sort > "$REP/worklist-A.txt"
awk -F'\t' '$1=="M"{print $2}' "$REP/worklist-full.txt" | LC_ALL=C sort > "$REP/worklist-M.txt"
awk -F'\t' '$1=="D"{print $2}' "$REP/worklist-full.txt" | LC_ALL=C sort > "$REP/worklist-D.txt"

echo "=== nach DROP-Filter uebrig ==="
printf 'A (Eigencode) : %s\n' "$(wc -l < "$REP/worklist-A.txt")"
printf 'M (Eingriffe) : %s\n' "$(wc -l < "$REP/worklist-M.txt")"
printf 'D (Loeschung) : %s\n' "$(wc -l < "$REP/worklist-D.txt")"
echo
echo "=== A-Dateien nach Verzeichnis ==="
awk -F/ '{NF--; print}' OFS=/ "$REP/worklist-A.txt" | sort | uniq -c | sort -rn | head -20
echo
echo "=== A-Dateien nach Typ ==="
awk -F. '{print $NF}' "$REP/worklist-A.txt" | sort | uniq -c | sort -rn
echo
echo "=== M-Eingriffe nach Subsystem ==="
awk -F/ '{if(NF>=3) print $1"/"$2"/"$3; else print $0}' "$REP/worklist-M.txt" | sort | uniq -c | sort -rn | head -15