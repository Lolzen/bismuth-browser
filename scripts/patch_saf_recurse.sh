#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/base/files/file_enumerator_posix.cc

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f).read()
old = "            pending_paths_.push(info.content_uri_);"
new = ("            if (root_path_.IsVirtualDocumentPath()) {\n"
       "              pending_paths_.push(root_path_.Append(info.filename_));\n"
       "            } else {\n"
       "              pending_paths_.push(info.content_uri_);\n"
       "            }")
if s.count(old) != 1:
    print("Muster nicht eindeutig:", s.count(old))
    sys.exit(1)
open(f, "w").write(s.replace(old, new, 1))
print("ok")
PY

cd "$S"
git diff base/files/file_enumerator_posix.cc