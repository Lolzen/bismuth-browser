import sys
D = "/home/gee/kiwi-rebase/build/chromium/src/"
D += "chrome/browser/extensions/api/developer_private/"
F = D + "developer_private_functions.cc"
s = open(F).read()

a = """      browser_context()->GetPath()
          .AppendASCII("UnpackedExtensions")"""
b = """      // One level above the profile. Copies kept inside the profile kept
      // vanishing without any Chromium log entry, from 149 onwards; the
      // profile is Chromium's own territory and it tidies up what it does
      // not recognise. This sits next to the component directories instead.
      browser_context()->GetPath()
          .DirName()
          .AppendASCII("BismuthExtensions")"""

if "BismuthExtensions" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")