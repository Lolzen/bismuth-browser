#!/usr/bin/env bash
SRC=/home/gee/kiwi-rebase/upstream/src.next
DEST=/home/gee/kiwi-rebase/patches/by-file
ANCHOR=b2a61e552c94

echo "=== Verzeichnisinhalt ==="
echo "Eintraege gesamt : $(ls -A "$DEST" | wc -l)"
echo "*.patch          : $(ls -1 "$DEST"/*.patch 2>/dev/null | wc -l)"
echo "leere Patches    : $(find "$DEST" -maxdepth 1 -name '*.patch' -empty | wc -l)"
echo "Nicht-Patch-Dateien:"
ls -A "$DEST" | grep -v '\.patch$' | head

echo
echo "=== Erwartung aus dem Diff ==="
cd "$SRC"
git -c core.quotePath=false diff --name-only "$ANCHOR"..kiwi | wc -l

echo
echo "=== Namenskollisionen nach tr-Mapping ==="
git -c core.quotePath=false diff --name-only "$ANCHOR"..kiwi \
  | tr '/' '_' | LC_ALL=C sort | uniq -d | wc -l

echo
echo "=== Erwartete Namen, die im Verzeichnis fehlen ==="
git -c core.quotePath=false diff --name-only "$ANCHOR"..kiwi \
  | tr '/' '_' | sed 's|$|.patch|' | LC_ALL=C sort -u > /tmp/expected.txt
ls -1 "$DEST" | grep '\.patch$' | LC_ALL=C sort > /tmp/actual.txt
echo "erwartet (unique): $(wc -l < /tmp/expected.txt)"
echo "vorhanden        : $(wc -l < /tmp/actual.txt)"
echo "--- fehlen: ---"
LC_ALL=C comm -23 /tmp/expected.txt /tmp/actual.txt
echo "--- unerwartet vorhanden: ---"
LC_ALL=C comm -13 /tmp/expected.txt /tmp/actual.txt

echo
echo "=== Beweis der Vollstaendigkeit ==="
if [ -d /tmp/kiwi-sanity ]; then
  git -C /tmp/kiwi-sanity diff --shortstat
else
  echo "Worktree /tmp/kiwi-sanity existiert nicht"
fi