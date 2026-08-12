#!/usr/bin/env bash
P=chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/TabListCoordinator.java
for T in 110.0.5481.77 115.0.5790.170 120.0.6099.216 125.0.6422.142 130.0.6723.116 135.0.7049.95 140.0.7339.80 145.0.7632.60 149.0.7827.238; do
  U="https://chromium.googlesource.com/chromium/src/+/refs/tags/$T/$P?format=TEXT"
  if curl -sf "$U" -o /tmp/tlc.b64; then
    if base64 -d < /tmp/tlc.b64 | grep -q 'TabListMode.LIST'; then
      echo "$T  LIST vorhanden"
    else
      echo "$T  LIST WEG"
    fi
  else
    echo "$T  Datei nicht gefunden"
  fi
  sleep 0.3
done