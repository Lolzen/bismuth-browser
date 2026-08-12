import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabSwitcherPaneCoordinatorFactory.java")
s = open(F).read()
a = "        mMode = TabListCoordinator.TabListMode.GRID;"
b = "        mMode = TabListCoordinator.TabListMode.LIST;  // TEST"
if b in s:
    print("schon gesetzt")
    sys.exit(0)
if a not in s:
    print("Anker nicht gefunden")
    sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok - Modus fest auf LIST")