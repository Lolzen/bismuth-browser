#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/extensions/common/extension_l10n_util.cc

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f).read()
old = """  if (!locales_path.AppendRelativePath(locale_path, &relative_path)) {
    NOTREACHED();
  }"""
new = """  if (!locales_path.AppendRelativePath(locale_path, &relative_path)) {
    LOG(ERROR) << "[LOCALEDBG] locales_path=" << locales_path.value()
               << " locale_path=" << locale_path.value();
    return true;
  }"""
if old not in s:
    print("Muster nicht gefunden")
    sys.exit(1)
open(f, "w").write(s.replace(old, new, 1))
print("ok")
PY

cd "$S"
git diff --stat extensions/common/extension_l10n_util.cc