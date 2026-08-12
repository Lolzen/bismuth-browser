import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListContainerViewBinder.java")
s = open(F).read()

a = "        assert model.get(MODE) == TabListMode.GRID;"
b = ("        // Only the grid mode centers cards via span count; list mode has no offset.\n"
     "        if (model.get(MODE) != TabListMode.GRID) return 0;")

if "list mode has no offset" in s:
    print("schon erledigt")
    sys.exit(0)
if s.count(a) != 1:
    print("Anker nicht eindeutig, gefunden:", s.count(a))
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")