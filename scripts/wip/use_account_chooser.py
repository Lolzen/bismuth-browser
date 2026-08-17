import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/components/signin/public/"
     "android/java/src/org/chromium/components/signin/"
     "SystemAccountManagerDelegate.java")
s = open(F).read()

a = """        AccountManagerCallback<Bundle> managerCallback =
                future -> {
                    try {
                        Bundle bundle = future.getResult();
                        callback.onResult(bundle.getParcelable(AccountManager.KEY_INTENT));
                    } catch (OperationCanceledException | IOException | AuthenticatorException e) {
                        Log.e(TAG, "Error while creating an intent to add an account: ", e);
                        callback.onResult(null);
                    }
                };
        mAccountManager.addAccount(
                GOOGLE_ACCOUNT_TYPE, null, null, null, null, managerCallback, null);"""

b = """        // Offer the accounts already on the device instead of forcing a new one.
        // Picking an account here also grants this app visibility of it, which
        // getAccountsByType otherwise withholds from apps Google has not signed.
        callback.onResult(
                AccountManager.newChooseAccountIntent(
                        null,
                        null,
                        new String[] {GOOGLE_ACCOUNT_TYPE},
                        null,
                        null,
                        null,
                        null));"""

if "newChooseAccountIntent" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")