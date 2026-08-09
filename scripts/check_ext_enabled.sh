#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
cd "$S" || exit 1

echo "=== Extension-bezogene GN-Args ==="
gn args out/Vanilla --list --short | grep -i extension

echo
echo "=== Wer referenziert die Datei? ==="
gn refs out/Vanilla //extensions/common/extension_features.cc 2>&1 | head -20

echo
echo "=== Buildflag-Definitionen ==="
cat extensions/buildflags/BUILD.gn