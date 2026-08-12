import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/extensions/api/"
     "developer_private/developer_private_functions.cc")
s = open(F).read()

if "staging" in s:
    print("schon erledigt"); sys.exit(0)

a = """  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to)) {
    LOG(ERROR) << "[COPYDBG] cannot create destination";
    return false;
  }"""
b = """  // Copy into a staging directory and only swap it in on success, so a
  // failed attempt cannot destroy a previously working copy.
  const base::FilePath staging = to.AddExtensionASCII("staging");
  base::DeletePathRecursively(staging);
  if (!base::CreateDirectory(staging)) {
    LOG(ERROR) << "[COPYDBG] cannot create staging directory";
    return false;
  }"""
if a not in s:
    print("Anker 1 fehlt"); sys.exit(1)
s = s.replace(a, b, 1)

a2 = "    base::FilePath target = to;"
b2 = "    base::FilePath target = staging;"
if a2 not in s:
    print("Anker 2 fehlt"); sys.exit(1)
s = s.replace(a2, b2, 1)

a3 = '''  LOG(ERROR) << "[COPYDBG] done, " << copied << " files";
  return true;'''
b3 = '''  base::DeletePathRecursively(to);
  if (!base::Move(staging, to)) {
    LOG(ERROR) << "[COPYDBG] swap failed";
    return false;
  }
  LOG(ERROR) << "[COPYDBG] done, " << copied << " files";
  return true;'''
if a3 not in s:
    print("Anker 3 fehlt"); sys.exit(1)
s = s.replace(a3, b3, 1)

open(F, "w").write(s)
print("ok")