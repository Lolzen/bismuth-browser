#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== Feature-Flags rund um MV2 ==="
git grep -n "ManifestV2" -- extensions/common/extension_features.cc
git grep -n "ManifestV2" -- chrome/browser/extensions/extension_features.cc

echo
echo "=== Dateien mit MV2-Bezug ==="
git grep -l "ManifestV2\|kMV2\|MV2Experiment" -- extensions/ chrome/browser/extensions/

echo
echo "=== Manifest-Versionspruefung ==="
git grep -n "kModernManifestVersion\|manifest_version" -- extensions/common/manifest.cc
git grep -n "manifest_version" -- extensions/common/extension.cc

echo
echo "=== Deprecation-Manager ==="
ls chrome/browser/extensions/ | grep -i "manifest_v2\|mv2"