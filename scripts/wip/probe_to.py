import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """      LOG(ERROR) << "[COPYDBG] " << copied << " files manifest="
                 << base::PathExists(to.AppendASCII("manifest.json"))
                 << " last=" << target.value();"""
b = """      LOG(ERROR) << "[COPYDBG] " << copied << " files manifest="
                 << base::PathExists(to.AppendASCII("manifest.json"))
                 << " checked=" << to.AppendASCII("manifest.json").value()
                 << " to_exists=" << base::DirectoryExists(to);"""

if "checked=" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")