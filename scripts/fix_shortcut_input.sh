#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
F=$S/ui/webui/resources/cr_components/cr_shortcut_input/BUILD.gn

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f).read()

imp_old = 'import("//ui/webui/webui_features.gni")'
imp_new = imp_old + '\nimport("//extensions/buildflags/buildflags.gni")'

a_old = "assert((!is_android && !is_ios) || enable_webui_ntp || is_desktop_android)"
a_new = ("assert((!is_android && !is_ios) || enable_webui_ntp || "
         "is_desktop_android || enable_desktop_android_extensions)")

if imp_old not in s or a_old not in s:
    print("Muster nicht gefunden")
    sys.exit(1)

s = s.replace(imp_old, imp_new, 1).replace(a_old, a_new, 1)
open(f, 'w').write(s)
print("ok")
PY

cd "$S"
git diff --stat