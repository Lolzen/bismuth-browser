import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/extensions/api/"
     "developer_private/developer_private_functions.cc")
s = open(F).read()

pairs = [
("""      if (!base::CreateDirectory(target)) {
        return false;
      }""",
 """      if (!base::CreateDirectory(target)) {
        LOG(ERROR) << "[COPYDBG] mkdir failed " << target.value();
        return false;
      }"""),
("""      if (!n) {
        return false;
      }""",
 """      if (!n) {
        LOG(ERROR) << "[COPYDBG] read failed " << p.value();
        return false;
      }"""),
("""    if (!base::WriteFile(target, data)) {
      return false;
    }""",
 """    if (!base::WriteFile(target, data)) {
      LOG(ERROR) << "[COPYDBG] write failed " << target.value();
      return false;
    }"""),
]

for a, b in pairs:
    if b.split("\n")[1].strip() in s:
        continue
    if a not in s:
        print("Anker fehlt:", a.split("\n")[0].strip())
        sys.exit(1)
    s = s.replace(a, b, 1)

open(F, "w").write(s)
print("ok - drei Pfade instrumentiert")