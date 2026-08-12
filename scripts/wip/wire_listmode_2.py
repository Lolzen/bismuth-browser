import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabListCoordinator.java")
s = open(F).read()

if "TabListViewBinder::bindTab" in s:
    print("schon erledigt")
    sys.exit(0)

a = """                    TabStripViewBinder::bind);
        } else {"""

b = """                    TabStripViewBinder::bind);
        } else if (mMode == TabListMode.LIST) {
            mAdapter.registerType(
                    UiType.TAB,
                    parent -> {
                        ViewLookupCachingFrameLayout group =
                                (ViewLookupCachingFrameLayout)
                                        LayoutInflater.from(activity)
                                                .inflate(
                                                        R.layout.tab_list_card_item,
                                                        parentView,
                                                        false);
                        group.setClickable(true);
                        return group;
                    },
                    TabListViewBinder::bindTab);
        } else {"""

if a not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

open(F, "w").write(s.replace(a, b, 1))
print("ok")