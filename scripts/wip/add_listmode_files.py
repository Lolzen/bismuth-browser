import os, re, sys

S = "/home/gee/kiwi-rebase/build/chromium/src"
T = (S + "/chrome/android/features/tab_ui/java/src/org/chromium/"
     "chrome/browser/tasks/tab_management")
L = S + "/chrome/android/features/tab_ui/java/res/layout"
R = "/home/gee/kiwi-rebase/reports/list-reference-138.0.7204.310"

# --- Layout ---
src = open(R + "/tab_list_card_item.xml").read()
open(L + "/tab_list_card_item.xml", "w").write(src)
print("Layout gesetzt")

# --- Java ---
renames = [
    ("import org.chromium.chrome.browser.tab_ui.TabUiThemeUtils;",
     "import org.chromium.chrome.browser.tab_ui.TabCardThemeUtil;"),
    ("TabUiThemeUtils.", "TabCardThemeUtil."),
    ("import org.chromium.chrome.browser.tasks.tab_management."
     "TabListMediator.TabActionButtonData.TabActionButtonType;",
     "import org.chromium.chrome.browser.tasks.tab_management."
     "TabActionButtonData.TabActionButtonType;"),
    ("import org.chromium.chrome.browser.tasks.tab_management."
     "TabListMediator.TabActionButtonData;\n", ""),
    ("import org.chromium.chrome.browser.tasks.tab_management."
     "TabListMediator.TabActionListener;\n", ""),
    ("TabListMediator.TabActionButtonData", "TabActionButtonData"),
    ("TabListMediator.TabActionListener", "TabActionListener"),
    ("import androidx.annotation.Nullable;",
     "import org.chromium.build.annotations.NullMarked;\n"
     "import org.chromium.build.annotations.Nullable;"),
]

for name in ["TabListView.java", "TabListViewBinder.java"]:
    s = open(R + "/" + name).read()
    for a, b in renames:
        s = s.replace(a, b)
    # @NullMarked vor die Klassendeklaration
    cls = re.search(r"^(class|public class) " + name[:-5], s, re.M)
    if cls and "@NullMarked" not in s:
        s = s[:cls.start()] + "@NullMarked\n" + s[cls.start():]
    open(T + "/" + name, "w").write(s)
    print("gesetzt:", name)

# --- BUILD.gn ---
B = S + "/chrome/android/features/tab_ui/BUILD.gn"
g = open(B).read()
anchor = '"java/src/org/chromium/chrome/browser/tasks/tab_management/TabStripViewBinder.java",'
if anchor not in g:
    print("BUILD.gn-Anker nicht gefunden - bitte manuell eintragen")
    sys.exit(1)
add = (anchor + "\n"
       '    "java/src/org/chromium/chrome/browser/tasks/tab_management/TabListView.java",\n'
       '    "java/src/org/chromium/chrome/browser/tasks/tab_management/TabListViewBinder.java",')
if "TabListViewBinder.java" not in g:
    g = g.replace(anchor, add, 1)
    open(B, "w").write(g)
    print("BUILD.gn ergaenzt")
else:
    print("BUILD.gn schon ergaenzt")