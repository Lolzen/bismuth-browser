import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/src/org/"
     "chromium/chrome/browser/ChromeTabbedActivity.java")
s = open(F).read()

a = """            ExtensionsToolbarCoordinator coordinator =
                    getToolbarManager().getExtensionsToolbarCoordinator();
            coordinator.showExtensionsMenu();
            RecordUserAction.record("MobileMenuExtensionsMenu");"""

b = """            ExtensionsToolbarCoordinator coordinator =
                    getToolbarManager().getExtensionsToolbarCoordinator();
            // The extensions toolbar is only created for tablet-sized layouts,
            // so on a phone this is null and tapping the item would crash.
            if (coordinator != null) {
                coordinator.showExtensionsMenu();
                RecordUserAction.record("MobileMenuExtensionsMenu");
            }"""

if "only created for tablet-sized layouts" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")