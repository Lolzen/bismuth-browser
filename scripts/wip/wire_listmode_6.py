import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListContainerViewBinder.java")
s = open(F).read()

a = """            assumeNonNull((LinearLayoutManager) recyclerView.getLayoutManager())
                    .scrollToPositionWithOffset(index, offset);"""
b = """            LinearLayoutManager initialScrollLayoutManager =
                    (LinearLayoutManager) recyclerView.getLayoutManager();
            if (initialScrollLayoutManager != null) {
                initialScrollLayoutManager.scrollToPositionWithOffset(index, offset);
            }"""

if "initialScrollLayoutManager" in s:
    print("schon erledigt")
    sys.exit(0)
if a not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

s = s.replace(a, b, 1)

a2 = """                        assumeNonNull(layoutManager);
                        int start = layoutManager.findFirstCompletelyVisibleItemPosition();"""
b2 = """                        if (layoutManager == null) return new Pair<>(0, 0);
                        int start = layoutManager.findFirstCompletelyVisibleItemPosition();"""
if a2 in s:
    s = s.replace(a2, b2, 1)
    print("zweite Stelle mit abgesichert")

open(F, "w").write(s)
print("ok")