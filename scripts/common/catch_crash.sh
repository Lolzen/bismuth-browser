#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
ADB=$S/third_party/android_sdk/public/platform-tools/adb
command -v adb >/dev/null && ADB=adb

echo ">> Logcat wird geleert. Danach die Seite aufrufen bis es kracht."
"$ADB" logcat -c
echo ">> Enter druecken, sobald der Absturz da war."
read -r _

"$ADB" logcat -d > /tmp/crash.log
echo "Zeilen: $(wc -l < /tmp/crash.log)"

echo
echo "=== Signale und Abstuerze ==="
grep -iE "SIGSEGV|SIGABRT|SIGBUS|Fatal signal|FATAL:" /tmp/crash.log | tail -20

echo
echo "=== Speicher ==="
grep -iE "lowmemorykiller|lmkd|Out of memory|OOM|kill.*renderer" /tmp/crash.log | tail -20

echo
echo "=== Chromium-Meldungen ==="
grep -iE "chromium|cr_|sandbox|renderer" /tmp/crash.log | tail -40