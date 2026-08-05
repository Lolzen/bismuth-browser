#!/usr/bin/env bash
# verify_tree.sh <git-ref> <chromium-tag> [anzahl]
set -uo pipefail
REF="${1:?git-ref angeben}"
TAG="${2:?Chromium-Tag angeben}"
N="${3:-40}"
SRC=/home/gee/kiwi-rebase/upstream/src.next
OUT=/home/gee/kiwi-rebase/reports/verify-$TAG-$(echo "$REF" | cut -c1-12).txt
BASE="https://chromium.googlesource.com/chromium/src/+/refs/tags/$TAG"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$SRC"; : > "$OUT"

git ls-tree -r --name-only "$REF" \
  | grep -Ev '\.(png|jpg|jpeg|webp|ico|ttf|otf|zip|jar|so)$' \
  | grep -Ev '^(\.github|\.build|toolbox)/' \
  | shuf -n "$N" \
  | while read -r f; do
      if ! curl -sf "$BASE/$f?format=TEXT" -o "$TMP/b64"; then
        echo "MISSING  $f" >> "$OUT"; sleep 0.15; continue
      fi
      base64 -d < "$TMP/b64" > "$TMP/remote"
      git show "$REF:$f" > "$TMP/local" 2>/dev/null
      if cmp -s "$TMP/remote" "$TMP/local"; then
        echo "MATCH    $f" >> "$OUT"
      else
        echo "DIFF     $f" >> "$OUT"
      fi
      sleep 0.15
    done

awk '{print $1}' "$OUT" | sort | uniq -c