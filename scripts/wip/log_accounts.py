import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/components/signin/public/"
     "android/java/src/org/chromium/components/signin/"
     "SystemAccountManagerDelegate.java")
s = open(F).read()

a = """    public Account[] getAccountsSynchronous() throws AccountManagerDelegateException {
        return mAccountManager.getAccountsByType(GOOGLE_ACCOUNT_TYPE);
    }"""
b = """    public Account[] getAccountsSynchronous() throws AccountManagerDelegateException {
        Account[] accounts = mAccountManager.getAccountsByType(GOOGLE_ACCOUNT_TYPE);
        Log.i(TAG, "[ACCTDBG] visible accounts: " + accounts.length);
        return accounts;
    }"""

if "ACCTDBG" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")