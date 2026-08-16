import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

if "manifest missing in temp" in s:
    print("schon erledigt"); sys.exit(0)

a1 = """  base::DeletePathRecursively(to.AddExtensionASCII("staging"));
  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to)) {
    LOG(ERROR) << "[COPYDBG] cannot create destination";
    return false;
  }"""
b1 = """  // Build the copy outside the extensions area and move it into place in one
  // step, the way Chromium installs a CRX. Anything still under construction
  // inside the profile's extension folders can be swept away mid-copy.
  const base::FilePath temp =
      to.DirName().DirName().AppendASCII("Temp").Append(to.BaseName());
  base::DeletePathRecursively(temp);
  if (!base::CreateDirectory(temp)) {
    LOG(ERROR) << "[COPYDBG] cannot create temp directory";
    return false;
  }
  LOG(ERROR) << "[COPYDBG] temp " << temp.value();"""
if a1 not in s:
    print("FEHLER: Anker 1 fehlt"); sys.exit(1)
s = s.replace(a1, b1, 1)

n = s.count("    base::FilePath target = to;")
s = s.replace("    base::FilePath target = to;",
              "    base::FilePath target = temp;")
print("Zielvariable ersetzt:", n)

s = s.replace('to.AppendASCII("manifest.json")',
              'temp.AppendASCII("manifest.json")')

a3 = """  if (!base::PathExists(temp.AppendASCII("manifest.json"))) {
    LOG(ERROR) << "[COPYDBG] manifest missing after copy";
    return false;
  }"""
b3 = """  if (!base::PathExists(temp.AppendASCII("manifest.json"))) {
    LOG(ERROR) << "[COPYDBG] manifest missing in temp";
    return false;
  }
  base::DeletePathRecursively(to);
  if (!base::CreateDirectory(to.DirName())) {
    LOG(ERROR) << "[COPYDBG] cannot create parent";
    return false;
  }
  if (!base::Move(temp, to)) {
    LOG(ERROR) << "[COPYDBG] move into place failed";
    return false;
  }
  if (!base::PathExists(to.AppendASCII("manifest.json"))) {
    LOG(ERROR) << "[COPYDBG] manifest missing after move";
    return false;
  }"""
if a3 not in s:
    print("FEHLER: Anker 3 fehlt"); sys.exit(1)
s = s.replace(a3, b3, 1)

open(F, "w").write(s)
print("ok")