#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/base/files/file_enumerator_posix.cc

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f).read()
old = "  if (root_path_.IsContentUri() || root_path_.IsVirtualDocumentPath()) {"
new = "  if (root_path_.IsContentUri()) {"
if old not in s:
    print("Muster nicht gefunden")
    sys.exit(1)
open(f, "w").write(s.replace(old, new, 1))
print("ok")
PY

cd "$S"
git diff --stat base/files/file_enumerator_posix.cc