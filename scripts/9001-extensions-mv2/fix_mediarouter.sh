#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/chrome/browser/media/router/BUILD.gn

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
old = "if (!is_android || enable_desktop_android_extensions) {"
new = "if (!is_android || is_desktop_android) {"
s = open(f).read()
if old not in s:
    print("Muster nicht gefunden")
    sys.exit(1)
s = s.replace(old, new, 1)
open(f, 'w').write(s)
print("ok")
PY

cd "$S"
git diff --stat chrome/browser/media/router/BUILD.gn