#!/usr/bin/env bash
R=/home/gee/kiwi-rebase/reports/list-reference-138.0.7204.310
TAG=138.0.7204.310
B=https://chromium.googlesource.com/chromium/src/+/refs/tags/$TAG
P=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management

for f in TabListView.java TabListViewHolder.java; do
  if curl -sf "$B/$P/$f?format=TEXT" -o /tmp/x.b64; then
    base64 -d < /tmp/x.b64 > "$R/$f"
    echo "ok   $f  $(wc -l < "$R/$f") Zeilen"
  else
    echo "gibt es nicht: $f"
  fi
done