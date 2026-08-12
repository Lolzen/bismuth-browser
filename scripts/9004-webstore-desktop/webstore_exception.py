import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# ---- 1. globales Default-Einschalten unterbinden ----
F = B + "chrome/android/java/src/org/chromium/chrome/browser/ui/RootUiCoordinator.java"
s = open(F).read()
if "maybeSetWebStoreDesktopException" not in s:
    a = """        if (DeviceFormFactor.isWindowOnTablet(mWindowAndroid)
                && DesktopSiteUtils.maybeDefaultEnableGlobalSetting("""
    b = """        // Desktop site must stay off by default; is_desktop_android otherwise
        // makes every page render as desktop on a phone.
        if (false
                && DesktopSiteUtils.maybeDefaultEnableGlobalSetting("""
    if a not in s:
        print("FEHLER: Anker 1 fehlt"); sys.exit(1)
    s = s.replace(a, b, 1)

    a2 = "        DesktopSiteUtils.maybeDefaultEnableWindowSetting(mActivity, originalProfile);"
    b2 = (a2 + "\n"
          "        DesktopSiteUtils.maybeSetWebStoreDesktopException(originalProfile);")
    if a2 not in s:
        print("FEHLER: Anker 2 fehlt"); sys.exit(1)
    s = s.replace(a2, b2, 1)
    open(F, "w").write(s)
    print("ok RootUiCoordinator")

# ---- 2. exakte Host-Ausnahme ----
F = (B + "chrome/browser/ui/android/desktop_site/java/src/org/chromium/chrome/"
     "browser/desktop_site/DesktopSiteUtils.java")
s = open(F).read()
if "maybeSetWebStoreDesktopException" in s:
    print("DesktopSiteUtils schon da"); sys.exit(0)

if "import org.chromium.base.ContextUtils;" not in s:
    m = re.search(r"^import org\.chromium\.", s, re.M)
    s = s[:m.start()] + "import org.chromium.base.ContextUtils;\n" + s[m.start():]

anchor = "    public static boolean maybeDefaultEnableGlobalSetting("
add = '''    /**
     * The Chrome Web Store only serves its extension pages to desktop browsers. Set a one-time
     * exception scoped to that exact host - not a domain wildcard, which would also cover Search.
     *
     * @param profile The current {@link Profile}.
     */
    public static void maybeSetWebStoreDesktopException(Profile profile) {
        final String prefKey = "web_store_desktop_exception_v2";
        if (ContextUtils.getAppSharedPreferences().getBoolean(prefKey, false)) {
            return;
        }
        WebsitePreferenceBridge.setContentSettingCustomScope(
                profile,
                ContentSettingsType.REQUEST_DESKTOP_SITE,
                "chromewebstore.google.com",
                /* secondaryPattern= */ SITE_WILDCARD,
                ContentSetting.ALLOW);
        ContextUtils.getAppSharedPreferences().edit().putBoolean(prefKey, true).apply();
    }

'''
if anchor not in s:
    print("FEHLER: Anker 3 fehlt"); sys.exit(1)
open(F, "w").write(s.replace(anchor, add + anchor, 1))
print("ok DesktopSiteUtils")