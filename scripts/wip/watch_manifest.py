import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """    if (++copied % 100 == 0) {
      LOG(ERROR) << "[COPYDBG] " << copied << " files";
    }"""
b = """    if (++copied % 25 == 0) {
      LOG(ERROR) << "[COPYDBG] " << copied << " files manifest="
                 << base::PathExists(to.AppendASCII("manifest.json"))
                 << " last=" << target.value();
    }"""

if "files manifest=" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")