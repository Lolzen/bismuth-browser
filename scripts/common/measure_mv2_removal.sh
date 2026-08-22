#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
REP=/home/gee/kiwi-rebase/reports
FROM=149.0.7827.238
TO="${1:?Ziel-Tag angeben, z.B. 151.0.7799.60}"
cd "$S" || exit 1

git fetch --tags origin

echo "=== Commits in extensions/ zwischen $FROM und $TO ==="
git log --oneline "$FROM".."$TO" -- extensions/ chrome/browser/extensions/ | wc -l

echo
echo "=== davon mit MV2-Bezug ==="
git log --oneline "$FROM".."$TO" -- extensions/ chrome/browser/extensions/ | grep -iE "mv2|manifest v2|manifestv2" | tee "$REP/mv2-removal-commits.txt" | wc -l

echo
echo "=== Umfang dieser Commits ==="
cut -d' ' -f1 "$REP/mv2-removal-commits.txt" > /tmp/mv2sha.txt
git show --stat --format= $(tr '\n' ' ' < /tmp/mv2sha.txt) 2>/dev/null | tail -1

echo
echo "=== gelöschte Dateien mit MV2-Bezug ==="
git diff --diff-filter=D --name-only "$FROM".."$TO" -- extensions/ chrome/browser/extensions/ | grep -iE "mv2|manifest_v2"