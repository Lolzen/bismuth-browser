import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

if "Remove earlier copies" in s:
    print("schon erledigt"); sys.exit(0)

a = """  if (!base::PathExists(to.AppendASCII("manifest.json"))) {
    return false;
  }
  return true;"""

b = """  if (!base::PathExists(to.AppendASCII("manifest.json"))) {
    return false;
  }

  // Remove earlier copies of the same source folder. Chromium never deletes
  // the directory of an unpacked extension, and every load creates a new one,
  // so without this they pile up.
  const std::string current = to.BaseName().value();
  const std::string prefix = current.substr(0, current.find('-'));
  base::FileEnumerator siblings(
      to.DirName(), false, base::FileEnumerator::DIRECTORIES);
  for (base::FilePath p = siblings.Next(); !p.empty(); p = siblings.Next()) {
    const std::string name = p.BaseName().value();
    if (name != current && name.compare(0, prefix.size(), prefix) == 0) {
      base::DeletePathRecursively(p);
    }
  }

  return true;"""

if a not in s:
    print("FEHLER: Anker fehlt")
    print("Bitte zeigen: grep -n 'manifest.json' developer_private_functions.cc")
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")