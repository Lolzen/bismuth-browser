import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/extensions/browser/"
     "manifest_v2_handler.cc")
s = open(F).read()
a = "bool g_allow_mv2_for_testing = false;"
b = """// Bismuth keeps Manifest V2 supported. Chromium already has the switch for it
// and only flips it from tests; we leave it on. Setting it here rather than
// touching the feature flags makes it immune to flag expiry.
bool g_allow_mv2_for_testing = true;"""
if "Bismuth keeps Manifest V2 supported" in s:
    print("schon erledigt"); sys.exit(0)
if s.count(a) != 1:
    print("FEHLER, Treffer:", s.count(a)); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")