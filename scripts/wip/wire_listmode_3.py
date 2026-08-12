import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListCoordinator.java")
s = open(F).read()

a = "    private void updateGridCardLayout(int viewWidth) {"
b = ("    private void updateGridCardLayout(int viewWidth) {\n"
     "        // Only the grid mode uses a GridLayoutManager; bail out otherwise.\n"
     "        if (mMode != TabListMode.GRID) return;")

if "if (mMode != TabListMode.GRID) return;" in s:
    print("schon erledigt")
    sys.exit(0)
if a not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")