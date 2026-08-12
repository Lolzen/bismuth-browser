import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListRecyclerView.java")
s = open(F).read()

a = """        GridLayoutManager layoutManager = (GridLayoutManager) getLayoutManager();
        assumeNonNull(layoutManager);
        int spanCount = layoutManager.getSpanCount();"""

b = """        RecyclerView.LayoutManager tabListLayoutManager = getLayoutManager();
        // List mode uses a LinearLayoutManager, which is a single column.
        int spanCount =
                tabListLayoutManager instanceof GridLayoutManager
                        ? ((GridLayoutManager) tabListLayoutManager).getSpanCount()
                        : 1;"""

if "tabListLayoutManager" in s:
    print("schon erledigt")
    sys.exit(0)

n = s.count(a)
if n != 2:
    print("Anker nicht zweimal gefunden, sondern:", n)
    sys.exit(1)

open(F, "w").write(s.replace(a, b))
print("ok - beide Stellen ersetzt")