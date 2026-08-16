import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """  if (!base::PathExists(to.AppendASCII("manifest.json"))) {"""
b = """  // Top-level files can vanish while the copy is still running, so write them
  // once more at the very end, right before verifying the result.
  base::FileEnumerator root(from, false, base::FileEnumerator::FILES);
  int rewritten = 0;
  for (base::FilePath p = root.Next(); !p.empty(); p = root.Next()) {
    base::FilePath target = to;
    if (!from.AppendRelativePath(p, &target)) {
      continue;
    }
    base::File in(p, base::File::FLAG_OPEN | base::File::FLAG_READ);
    if (!in.IsValid()) {
      continue;
    }
    std::string data;
    std::vector<uint8_t> buf(65536);
    while (true) {
      std::optional<size_t> n = in.ReadAtCurrentPos(base::span(buf));
      if (!n || *n == 0) {
        break;
      }
      data.append(reinterpret_cast<const char*>(buf.data()), *n);
    }
    if (base::WriteFile(target, data)) {
      ++rewritten;
    }
  }
  LOG(ERROR) << "[COPYDBG] second pass rewrote " << rewritten << " root files";

  if (!base::PathExists(to.AppendASCII("manifest.json"))) {"""

if "second pass rewrote" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")