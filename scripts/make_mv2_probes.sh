#!/usr/bin/env bash
set -e
B=/home/gee/kiwi-rebase/probes
rm -rf "$B"; mkdir -p "$B/a-nobg" "$B/b-bg"

cat > "$B/a-nobg/manifest.json" <<'JSON'
{
  "manifest_version": 2,
  "name": "MV2 Probe A",
  "version": "1.0",
  "content_scripts": [
    { "matches": ["<all_urls>"], "js": ["cs.js"] }
  ]
}
JSON
echo 'console.log("[PROBE-A] content script running");' > "$B/a-nobg/cs.js"

cat > "$B/b-bg/manifest.json" <<'JSON'
{
  "manifest_version": 2,
  "name": "MV2 Probe B",
  "version": "1.0",
  "background": { "scripts": ["bg.js"], "persistent": true }
}
JSON
echo 'console.log("[PROBE-B] background page running");' > "$B/b-bg/bg.js"

echo "Sondierungen liegen unter $B"
ls -R "$B"