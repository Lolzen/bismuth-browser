import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """    if (!base::WriteFile(target, data)) {"""
b = """    if (target.BaseName().value() == "manifest.json") {
      bool ok = base::WriteFile(target, data);
      LOG(ERROR) << "[COPYDBG] manifest write ok=" << ok
                 << " size=" << data.size()
                 << " exists_after=" << base::PathExists(target)
                 << " path=" << target.value();
    }
    if (!base::WriteFile(target, data)) {"""

if "manifest write ok=" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")