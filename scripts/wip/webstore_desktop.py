import re, sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/ui/android/"
     "desktop_site/java/src/org/chromium/chrome/browser/desktop_site/"
     "DesktopSiteUtils.java")
s = open(F).read()

if "maybeDefaultEnableWebStoreDesktopSite" in s:
    print("schon da"); sys.exit(0)

if "import org.chromium.base.ContextUtils;" not in s:
    m = re.search(r"^import org\.chromium\.", s, re.M)
    s = s[:m.start()] + "import org.chromium.base.ContextUtils;\n" + s[m.start():]

anchor = """    public static boolean maybeDefaultEnableGlobalSetting("""
add = '''    /**
     * The Chrome Web Store only serves its extension pages to desktop browsers. Set a one-time
     * desktop site exception for the store domains so extensions can be installed without the
     * user switching the view by hand. The exception is a regular content setting and can be
     * removed by the user at any time.
     *
     * @param profile The current {@link Profile}.
     */
    public static void maybeDefaultEnableWebStoreDesktopSite(Profile profile) {
        final String prefKey = "web_store_desktop_exception_set";
        if (ContextUtils.getAppSharedPreferences().getBoolean(prefKey, false)) {
            return;
        }
        setRequestDesktopSiteContentSettingsForUrl(
                profile, new GURL("https://chromewebstore.google.com"), true);
        setRequestDesktopSiteContentSettingsForUrl(
                profile, new GURL("https://chrome.google.com"), true);
        ContextUtils.getAppSharedPreferences().edit().putBoolean(prefKey, true).apply();
    }

'''

if anchor not in s:
    print("Anker nicht gefunden"); sys.exit(1)

open(F, "w").write(s.replace(anchor, add + anchor, 1))
print("ok - Methode angelegt")