#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/extensions/browser/manifest_v2_experiment_manager.cc
cd "$S" || exit 1

echo "=== Zeilen 140-270 ==="
sed -n '140,270p' "$F"

echo
echo "=== Zeile 430-460 ==="
sed -n '430,460p' "$F"

echo
echo "=== wer setzt die Stufe global ==="
grep -rn "kExtensionManifestV2Unsupported" --include=*.cc --include=*.h .