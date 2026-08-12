import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"
     "TabSwitcherPaneCoordinator.java")
s = open(F).read()

if "skip it in list mode" in s:
    print("schon erledigt")
    sys.exit(0)

start = "            mPinnedTabsCoordinator =\n                    new PinnedTabStripCoordinator("
end = "            pinnedTabsContainer.addView(pinnedTabStripRecyclerView);"

i = s.find(start)
j = s.find(end)
if i < 0 or j < 0 or j < i:
    print("Bloeckgrenzen nicht gefunden")
    sys.exit(1)
j += len(end)

block = """            if (mode == TabListMode.LIST) {
                // The pinned tab strip assumes a GridLayoutManager, so skip it in list mode.
                mPinnedTabsCoordinator = null;
            } else {
                mPinnedTabsCoordinator =
                        new PinnedTabStripCoordinator(
                                mActivity,
                                parentView,
                                tabListCoordinator,
                                mTabGroupModelFilterSupplier,
                                tabBookmarkerSupplier,
                                bottomSheetController,
                                modalDialogManager,
                                onTabGroupCreation);
                mContainerViewModel.set(
                        TabListContainerProperties.IS_PINNED_TAB_STRIP_ANIMATING_SUPPLIER,
                        mPinnedTabsCoordinator.getIsVisibilityAnimationRunningSupplier());
                TabListRecyclerView pinnedTabStripRecyclerView =
                        mPinnedTabsCoordinator.getPinnedTabsRecyclerView();
                FrameLayout pinnedTabsContainer =
                        layout.findViewById(R.id.pinned_tabs_container);
                pinnedTabsContainer.addView(pinnedTabStripRecyclerView);
            }"""

s = s[:i] + block + s[j:]

a1 = """                                assert mPinnedTabsCoordinator != null;
                                if (isAnyTabPinned()) {"""
b1 = """                                if (mPinnedTabsCoordinator != null && isAnyTabPinned()) {"""
if a1 not in s:
    print("Anker onScrollStateChanged nicht gefunden")
    sys.exit(1)
s = s.replace(a1, b1, 1)

a2 = """        assert mPinnedTabsCoordinator != null;
        mPinnedTabsCoordinator.onScrolled();"""
b2 = """        if (mPinnedTabsCoordinator == null) return;
        mPinnedTabsCoordinator.onScrolled();"""
if a2 not in s:
    print("Anker updatePinnedTabsStripOnScroll nicht gefunden")
    sys.exit(1)
s = s.replace(a2, b2, 1)

open(F, "w").write(s)
print("ok - drei Stellen abgesichert")