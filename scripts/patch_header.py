import sys
H = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/"
     "extensions/api/developer_private/developer_private_functions.h")
s = open(H).read()
if "ContinueFileLoad" in s:
    print("schon vorhanden")
    sys.exit(0)
old = "  void StartFileLoad(const base::FilePath file_path);"
new = old + """
  void ContinueFileLoad(base::FilePath file_path);
  void OnCopyComplete(base::FilePath dest,
                      base::FilePath source,
                      bool success);"""
if old not in s:
    print("Anker nicht gefunden")
    sys.exit(1)
open(H, "w").write(s.replace(old, new, 1))
print("ok")