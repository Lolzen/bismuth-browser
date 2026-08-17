import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/components/signin/public/"
     "android/BUILD.gn")
s = open(F).read()

a = '    "java/src/org/chromium/components/signin/NullAccountManagerDelegate.java",'
b = (a + '\n    "java/src/org/chromium/components/signin/'
     'SystemAccountManagerDelegate.java",')

if "SystemAccountManagerDelegate.java" in s:
    print("schon erledigt"); sys.exit(0)
if s.count(a) != 1:
    print("FEHLER, Treffer:", s.count(a)); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")