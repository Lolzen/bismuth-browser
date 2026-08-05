#!/usr/bin/env bash
P=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/TabListCoordinator.java
R=https://chromium.googlesource.com/chromium/src

for M in 136 137 138 139; do
  T=$(git ls-remote --tags "$R" "${M}.0.*" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||' | sort -V | tail -1)
  if [ -z "$T" ]; then echo "$M  kein Tag gefunden"; continue; fi
  if curl -sf "$R/+/refs/tags/$T/$P?format=TEXT" -o /tmp/tlc.b64; then
    if base64 -d < /tmp/tlc.b64 | grep -q 'TabListMode.LIST'; then
      echo "$T  LIST vorhanden"
    else
      echo "$T  LIST WEG"
    fi
  else
    echo "$T  Datei nicht abrufbar"
  fi
  sleep 0.3
done