import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """  const base::FilePath staging = to.AddExtensionASCII("staging");
  base::DeletePathRecursively(staging);
  if (!base::CreateDirectory(staging)) {
    LOG(ERROR) << "[COPYDBG] cannot create staging directory";
    return false;
  }"""
b = """  base::DeletePathRecursively(to.AddExtensionASCII("staging"));
  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to)) {
    LOG(ERROR) << "[COPYDBG] cannot create destination";
    return false;
  }"""
if a not in s:
    print("FEHLER: Anker 1 fehlt"); sys.exit(1)
s = s.replace(a, b, 1)

a2 = "    base::FilePath target = staging;"
b2 = "    base::FilePath target = to;"
if a2 not in s:
    print("FEHLER: Anker 2 fehlt"); sys.exit(1)
s = s.replace(a2, b2, 1)

a3 = """  base::DeletePathRecursively(to);
  if (!base::Move(staging, to)) {
    LOG(ERROR) << "[COPYDBG] swap failed";
    return false;
  }
  LOG(ERROR)"""
b3 = """  if (!base::PathExists(to.AppendASCII("manifest.json"))) {
    LOG(ERROR) << "[COPYDBG] manifest missing after copy";
    return false;
  }
  LOG(ERROR)"""
if a3 not in s:
    print("FEHLER: Anker 3 fehlt"); sys.exit(1)
s = s.replace(a3, b3, 1)

open(F, "w").write(s)
print("ok")