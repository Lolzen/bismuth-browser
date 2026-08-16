import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """    base::FilePath target = to;
    if (!from.AppendRelativePath(p, &target)) {
      continue;
    }"""
b = """    base::FilePath target = to;
    if (!from.AppendRelativePath(p, &target)) {
      LOG(ERROR) << "[COPYDBG] skipped, no relative path: " << p.value();
      continue;
    }
    if (copied < 5 || target.DirName() == to) {
      LOG(ERROR) << "[COPYDBG] target " << target.value()
                 << " dir=" << traversal.GetInfo().IsDirectory();
    }"""

if "skipped, no relative path" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")