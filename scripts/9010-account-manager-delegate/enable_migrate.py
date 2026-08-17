import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/components/signin/public/"
     "base/signin_switches.cc")
s = open(F).read()

a = ("BASE_FEATURE(kMigrateAccountManagerDelegate, "
     "base::FEATURE_DISABLED_BY_DEFAULT);")
b = ("BASE_FEATURE(kMigrateAccountManagerDelegate, "
     "base::FEATURE_ENABLED_BY_DEFAULT);")

if b in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt - bitte zeigen:")
    print("  grep -n 'kMigrateAccountManagerDelegate' signin_switches.cc")
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")