import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/extensions/api/"
     "developer_private/developer_private_functions.cc")
s = open(F).read()
a = """    if (!base::WriteFile(target, data)) {
      LOG(ERROR) << "[COPYDBG] write failed " << target.value();
      return false;
    }"""
b = """    // The enumerator does not guarantee that a directory is reported before
    // the files inside it, so make sure the parent exists.
    if (!base::CreateDirectory(target.DirName())) {
      LOG(ERROR) << "[COPYDBG] mkdir parent failed " << target.DirName();
      return false;
    }
    if (!base::WriteFile(target, data)) {
      LOG(ERROR) << "[COPYDBG] write failed " << target.value()
                 << " size=" << data.size()
                 << " parent_exists=" << base::DirectoryExists(target.DirName());
      return false;
    }"""
if "mkdir parent failed" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")