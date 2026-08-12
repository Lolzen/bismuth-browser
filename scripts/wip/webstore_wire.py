import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/src/org/"
     "chromium/chrome/browser/ui/RootUiCoordinator.java")
s = open(F).read()

if "maybeDefaultEnableWebStoreDesktopSite" in s:
    print("schon verdrahtet"); sys.exit(0)

a = "        DesktopSiteUtils.maybeDefaultEnableWindowSetting(mActivity, originalProfile);"
b = (a + "\n"
     "        DesktopSiteUtils.maybeDefaultEnableWebStoreDesktopSite(originalProfile);")

if a not in s:
    print("Anker nicht gefunden"); sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")