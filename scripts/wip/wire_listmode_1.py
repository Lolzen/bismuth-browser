import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListCoordinator.java")
s = open(F).read()

# 1. Enum-Wert zurueckholen
a1 = "@IntDef({TabListMode.GRID, TabListMode.STRIP, TabListMode.NUM_ENTRIES})"
b1 = ("@IntDef({\n"
      "        TabListMode.GRID,\n"
      "        TabListMode.STRIP,\n"
      "        TabListMode.LIST,\n"
      "        TabListMode.NUM_ENTRIES\n"
      "    })")
a2 = "        // int LIST_DEPRECATED = 3;"
b2 = "        int LIST = 3;"

# 2. vertikaler LayoutManager
a3 = """            } else if (mMode == TabListMode.STRIP) {
                LinearLayoutManager layoutManager =
                        new LinearLayoutManager(activity, LinearLayoutManager.HORIZONTAL, false) {"""
b3 = """            } else if (mMode == TabListMode.STRIP || mMode == TabListMode.LIST) {
                LinearLayoutManager layoutManager =
                        new LinearLayoutManager(
                                activity,
                                mMode == TabListMode.LIST
                                        ? LinearLayoutManager.VERTICAL
                                        : LinearLayoutManager.HORIZONTAL,
                                false) {"""

# 3. Drag-and-drop auch im Listenmodus
a4 = "boolean modeAllowsDragAndDrop = mMode == TabListMode.GRID;"
b4 = ("boolean modeAllowsDragAndDrop =\n"
      "                mMode == TabListMode.GRID || mMode == TabListMode.LIST;")

for a, b, name in [(a1, b1, "IntDef"), (a2, b2, "LIST-Konstante"),
                   (a3, b3, "LayoutManager"), (a4, b4, "DragAndDrop")]:
    if b.split("\n")[0].strip() in s and a not in s:
        print("schon erledigt:", name)
        continue
    if a not in s:
        print("ANKER FEHLT:", name)
        sys.exit(1)
    s = s.replace(a, b, 1)
    print("ok:", name)

open(F, "w").write(s)