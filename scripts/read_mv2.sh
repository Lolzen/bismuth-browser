#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== scoped_test_mv2_enabler.cc ==="
cat chrome/browser/extensions/scoped_test_mv2_enabler.cc

echo
echo "=== Flag-Definitionen 110-150 ==="
sed -n '110,150p' extensions/common/extension_features.cc

echo
echo "=== Minimum-Manifestversionen ==="
grep -n "kMinimum.*ManifestVersion\|kMaximumSupported" extensions/common/manifest_constants.h

echo
echo "=== IsManifestSupported ==="
sed -n '95,160p' extensions/common/extension.cc

echo
echo "=== Experiment-Stufen ==="
cat extensions/browser/mv2_experiment_stage.h