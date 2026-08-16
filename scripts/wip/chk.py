import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """  LOG(ERROR) << "[COPYDBG] done, " << copied << " files";
  return true;"""
b = """  LOG(ERROR) << "[COPYDBG] done, " << copied << " files"
             << " manifest_exists="
             << base::PathExists(to.AppendASCII("manifest.json"))
             << " dir_exists=" << base::DirectoryExists(to);
  return true;"""

if "manifest_exists=" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")