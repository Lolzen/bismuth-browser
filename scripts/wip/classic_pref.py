import re, sys
S = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/")

PREF = ('ContextUtils.getAppSharedPreferences()\n'
        '                        .getBoolean("classic_tab_switcher", true)')

def add_import(s, imp):
    if imp in s:
        return s
    m = re.search(r"^import org\.chromium\.", s, re.M)
    return s[:m.start()] + imp + "\n" + s[m.start():]

# --- Mediator ---
F = S + "TabListMediator.java"
s = open(F).read()
a = """        // Classic tab switcher: a single column of full-width cards.
        final int newSpanCount = 1;"""
b = """        // Classic tab switcher: a single column of full-width cards.
        final boolean classic =
                ContextUtils.getAppSharedPreferences()
                        .getBoolean("classic_tab_switcher", true);
        final int newSpanCount = classic ? 1 : getSpanCount(screenWidthDp);"""
if "classic_tab_switcher" in s:
    print("Mediator schon erledigt")
elif a not in s:
    print("FEHLER: Mediator-Anker fehlt"); sys.exit(1)
else:
    s = add_import(s.replace(a, b, 1), "import org.chromium.base.ContextUtils;")
    open(F, "w").write(s)
    print("ok Mediator")

# --- Coordinator ---
F = S + "TabListCoordinator.java"
s = open(F).read()
a = "                mRecyclerView.addItemDecoration(new ClassicStyleItemDecoration());"
b = ("                if (ContextUtils.getAppSharedPreferences()\n"
     "                        .getBoolean(\"classic_tab_switcher\", true)) {\n"
     "                    mRecyclerView.addItemDecoration(new ClassicStyleItemDecoration());\n"
     "                }")
if "classic_tab_switcher" in s:
    print("Coordinator schon erledigt")
elif a not in s:
    print("FEHLER: Coordinator-Anker fehlt"); sys.exit(1)
else:
    s = add_import(s.replace(a, b, 1), "import org.chromium.base.ContextUtils;")
    open(F, "w").write(s)
    print("ok Coordinator")