import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"
KEY = "classic_tab_switcher_v2"

def add_import(s, imp):
    if imp in s:
        return s
    m = re.search(r"^import (androidx|android|org)\.", s, re.M)
    return s[:m.start()] + imp + "\n" + s[m.start():]

# ---- 1. XML ----
X = B + "chrome/android/java/res/xml/appearance_preferences.xml"
s = open(X).read()
if KEY not in s:
    add = ('    <org.chromium.components.browser_ui.settings.ChromeSwitchPreference\n'
           '        android:key="' + KEY + '"\n'
           '        android:persistent="false"\n'
           '        android:order="3"\n'
           '        android:title="Classic tab switcher"\n'
           '        android:summary="Single overlapping column of tab cards" />\n'
           '</PreferenceScreen>')
    open(X, "w").write(s.replace("</PreferenceScreen>", add, 1))
    print("ok XML")
else:
    print("XML schon da")

# ---- 2. Fragment mit Logging ----
F = (B + "chrome/android/java/src/org/chromium/chrome/browser/appearance/"
     "settings/AppearanceSettingsFragment.java")
s = open(F).read()
if KEY not in s:
    for imp in ["import androidx.preference.TwoStatePreference;",
                "import android.util.Log;",
                "import org.chromium.base.ContextUtils;"]:
        s = add_import(s, imp)
    a = "        SettingsUtils.addPreferencesFromResource(this, R.xml.appearance_preferences);"
    b = a + '''

        TwoStatePreference classicPref = findPreference("''' + KEY + '''");
        Log.i("CLASSICDBG", "findPreference -> " + classicPref);
        if (classicPref != null) {
            boolean current =
                    ContextUtils.getAppSharedPreferences().getBoolean("''' + KEY + '''", true);
            Log.i("CLASSICDBG", "initial value = " + current);
            classicPref.setChecked(current);
            classicPref.setOnPreferenceChangeListener(
                    (pref, newValue) -> {
                        Log.i("CLASSICDBG", "listener fired, newValue = " + newValue);
                        ContextUtils.getAppSharedPreferences()
                                .edit()
                                .putBoolean("''' + KEY + '''", (Boolean) newValue)
                                .apply();
                        return true;
                    });
        }'''
    if a not in s:
        print("FEHLER: Fragment-Anker fehlt"); sys.exit(1)
    open(F, "w").write(s.replace(a, b, 1))
    print("ok Fragment")
else:
    print("Fragment schon da")

# ---- 3. Leseseite ----
T = B + "chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"

F = T + "TabListMediator.java"
s = open(F).read()
if KEY not in s:
    a = "        final int newSpanCount = 1;"
    b = ('        final int newSpanCount =\n'
         '                ContextUtils.getAppSharedPreferences()\n'
         '                                .getBoolean("' + KEY + '", true)\n'
         '                        ? 1\n'
         '                        : getSpanCount(screenWidthDp);')
    if a not in s:
        print("FEHLER: Mediator-Anker fehlt"); sys.exit(1)
    s = add_import(s.replace(a, b, 1), "import org.chromium.base.ContextUtils;")
    open(F, "w").write(s)
    print("ok Mediator")

F = T + "TabListCoordinator.java"
s = open(F).read()
if KEY not in s:
    a = "                mRecyclerView.addItemDecoration(new ClassicStyleItemDecoration());"
    b = ('                if (ContextUtils.getAppSharedPreferences()\n'
         '                        .getBoolean("' + KEY + '", true)) {\n'
         '                    mRecyclerView.addItemDecoration(new ClassicStyleItemDecoration());\n'
         '                }')
    if a not in s:
        print("FEHLER: Coordinator-Anker fehlt"); sys.exit(1)
    s = add_import(s.replace(a, b, 1), "import org.chromium.base.ContextUtils;")
    open(F, "w").write(s)
    print("ok Coordinator")