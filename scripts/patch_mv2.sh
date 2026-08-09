#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/extensions/common/extension_features.cc

A="BASE_FEATURE(kExtensionManifestV2Unsupported, base::FEATURE_ENABLED_BY_DEFAULT);"
B="BASE_FEATURE(kExtensionManifestV2Unsupported, base::FEATURE_DISABLED_BY_DEFAULT);"
C="BASE_FEATURE(kExtensionManifestV2Disabled, base::FEATURE_ENABLED_BY_DEFAULT);"
D="BASE_FEATURE(kExtensionManifestV2Disabled, base::FEATURE_DISABLED_BY_DEFAULT);"

grep -qF "$A" "$F" || { echo "Zeile 1 nicht gefunden"; exit 1; }
grep -qF "$C" "$F" || { echo "Zeile 2 nicht gefunden"; exit 1; }

python3 - "$F" "$A" "$B" "$C" "$D" <<'PY'
import sys
f, a, b, c, d = sys.argv[1:6]
s = open(f).read()
s = s.replace(a, b).replace(c, d)
open(f, 'w').write(s)
PY

cd "$S"
git diff --stat
git diff extensions/common/extension_features.cc