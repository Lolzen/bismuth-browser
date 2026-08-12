#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== Verwendungen von kAllowLegacyMV2Extensions ==="
git grep -n "kAllowLegacyMV2Extensions"

echo
echo "=== Stufenberechnung ==="
grep -n "MV2ExperimentStage\|GetCurrentExperimentStage\|CalculateCurrentStage" extensions/browser/manifest_v2_experiment_manager.cc | head -30

echo
echo "=== AllowMV2ExtensionsForTesting ==="
grep -n -A20 "AllowMV2ExtensionsForTesting" extensions/browser/manifest_v2_experiment_manager.cc

echo
echo "=== wo die Flags abgefragt werden ==="
git grep -n "kExtensionManifestV2Unsupported\|kExtensionManifestV2Disabled" -- extensions/brows