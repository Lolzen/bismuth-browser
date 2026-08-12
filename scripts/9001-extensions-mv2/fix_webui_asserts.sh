#!/usr/bin/env bash
set -e
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S"

A_OLD='assert((!is_android && !is_ios) || enable_webui_ntp || is_desktop_android)'

git grep -l -F "$A_OLD" -- '*.gn' > /tmp/assert_files.txt
echo "betroffene Dateien: $(wc -l < /tmp/assert_files.txt)"
cat /tmp/assert_files.txt

python3 - <<'PY'
a_old = ('assert((!is_android && !is_ios) || enable_webui_ntp || '
         'is_desktop_android)')
a_new = ('assert((!is_android && !is_ios) || enable_webui_ntp || '
         'is_desktop_android || enable_desktop_android_extensions)')
imp = 'import("//extensions/buildflags/buildflags.gni")'

for line in open('/tmp/assert_files.txt'):
    f = line.strip()
    if not f:
        continue
    s = open(f).read()
    if a_old not in s:
        continue
    if imp not in s:
        s = s.replace(a_old, imp + '\n' + a_new, 1)
    else:
        s = s.replace(a_old, a_new, 1)
    open(f, 'w').write(s)
    print('gepatcht:', f)
PY

git diff --stat