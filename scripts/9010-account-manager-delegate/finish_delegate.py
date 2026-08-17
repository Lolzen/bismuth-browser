import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# --- 1. Protokollzeile entfernen ---
F = (B + "components/signin/public/android/java/src/org/chromium/components/"
     "signin/SystemAccountManagerDelegate.java")
s = open(F).read()
a = """        Account[] a = mAccountManager.getAccountsByType(GoogleAuthUtil.GOOGLE_ACCOUNT_TYPE);
        Log.e(TAG, "[ACCTDBG] getAccountsSynchronous -> " + a.length);
        return a;"""
b = """        return mAccountManager.getAccountsByType(GoogleAuthUtil.GOOGLE_ACCOUNT_TYPE);"""
if "ACCTDBG" in s:
    if a not in s:
        print("FEHLER: Protokoll-Anker fehlt"); sys.exit(1)
    open(F, "w").write(s.replace(a, b, 1))
    print("ok Protokollzeile entfernt")
else:
    print("Protokollzeile schon weg")

# --- 2. Feature standardmaessig aus ---
F = B + "components/signin/public/base/signin_switches.cc"
s = open(F).read()
m = re.search(r"BASE_FEATURE\(kMigrateAccountManagerDelegate,\s*"
              r"base::FEATURE_(\w+)_BY_DEFAULT\);", s)
if not m:
    print("FEHLER: BASE_FEATURE nicht gefunden - bitte melden")
    sys.exit(1)
print("gefunden:", m.group(0).replace("\n", " "))
if m.group(1) == "DISABLED":
    print("schon deaktiviert")
else:
    s = s[:m.start()] + m.group(0).replace("ENABLED", "DISABLED") + s[m.end():]
    open(F, "w").write(s)
    print("ok Feature deaktiviert")