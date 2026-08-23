import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/feed/android/"
     "java/src/org/chromium/chrome/browser/feed/FeedFeatures.java")
s = open(F).read()

a = """        return !DeviceInfo.isDesktop()
                && FeedServiceBridge.isEnabled()
                && isFeedEnabledByDse(profile);"""
b = """        // Bismuth builds with is_desktop_android, so DeviceInfo reports a
        // desktop and the feed would switch itself off. The feed is fully
        // compiled in and works, so the check is dropped here.
        return FeedServiceBridge.isEnabled() && isFeedEnabledByDse(profile);"""

if "Bismuth builds with is_desktop_android" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")