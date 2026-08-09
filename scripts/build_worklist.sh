#!/usr/bin/env bash
set -e
REP=/home/gee/kiwi-rebase/reports
SRC=/home/gee/kiwi-rebase/upstream/src.next
ANCHOR=b2a61e552c94

DROP='\.png$|^\.github/|^\.gitignore$|^\.build/|^toolbox/|kiwi_logo|^VERSION$|^KIWI_VERSION$|^CHROMIUM_VERSION$|fetch_from_upstream|^remoting/|signin/ui/|browser/ui/extensions/|StartSurface|NewTabTile|PseudoTab|/values-[a-z]{2}(-r[A-Z]{2})?/'

cd "$SRC"
git -c core.quotePath=false diff --name-status "$ANCHOR"..kiwi \
  | awk -F'\t' -v d="$DROP" '$2 !~ d {print}' > "$REP/worklist-full.txt"

for s in A M D; do
  awk -F'\t' -v s="$s" '$1==s{print $2}' "$REP/worklist-full.txt" \
    | LC_ALL=C sort > "$REP/worklist-$s.txt"
done

echo "=== uebrig ==="
printf 'A %s   M %s   D %s\n' \
  "$(wc -l < "$REP/worklist-A.txt")" \
  "$(wc -l < "$REP/worklist-M.txt")" \
  "$(wc -l < "$REP/worklist-D.txt")"
echo
echo "=== A-Dateien vollstaendig ==="
cat "$REP/worklist-A.txt"