import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """    base::FileEnumerator counter(from, true, base::FileEnumerator::FILES);
    for (base::FilePath p = counter.Next(); !p.empty(); p = counter.Next()) {
      ++total;
    }"""
b = """    // Over SAF the requested type is passed through to the directory
    // listing, so asking for FILES alone hides the subdirectories and the
    // recursion never descends. Ask for both and skip directories here.
    base::FileEnumerator counter(
        from, true,
        base::FileEnumerator::FILES | base::FileEnumerator::DIRECTORIES);
    for (base::FilePath p = counter.Next(); !p.empty(); p = counter.Next()) {
      if (!counter.GetInfo().IsDirectory()) {
        ++total;
      }
    }"""

if "hides the subdirectories" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")