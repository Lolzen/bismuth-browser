#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
OUT=/home/gee/kiwi-rebase/reports/mv2-150
FROM=149.0.7827.238
TO=150.0.7871.249
mkdir -p "$OUT"
cd "$S" || exit 1

git log --oneline "$FROM..$TO" -i \
  --grep="ManifestV2" --grep="MV2" --grep="manifest_v2" \
  -- extensions/ > "$OUT/commits.txt"

echo "=== Commits ==="
cat "$OUT/commits.txt"
echo

cut -d' ' -f1 "$OUT/commits.txt" > "$OUT/hashes.txt"

n=0
while read -r h; do
  [ -z "$h" ] && continue
  n=$((n+1))
  git show "$h" > "$OUT/$n-$h.diff"
  echo "--- $n: $h ---"
  git show --stat --oneline "$h" | head -12
  echo
done < "$OUT/hashes.txt"

echo "Diffs liegen in $OUT"