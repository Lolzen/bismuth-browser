import re, sys

# --- XML: Persistenz abschalten ---
X = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/res/"
     "xml/appearance_preferences.xml")
s = open(X).read()
if 'android:persistent="false"' not in s:
    a = '        android:key="classic_tab_switcher"'
    b = ('        android:key="classic_tab_switcher"\n'
         '        android:persistent="false"')
    if a not in s:
        print("FEHLER: XML-Anker fehlt"); sys.exit(1)
    s = s.replace(a, b, 1).replace(
        '        android:defaultValue="true"\n', '', 1)
    open(X, "w").write(s)
    print("ok XML")
else:
    print("XML schon erledigt")

# --- Fragment: selbst lesen und schreiben ---
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/src/"
     "org/chromium/chrome/browser/appearance/settings/"
     "AppearanceSettingsFragment.java")
s = open(F).read()
if "classic_tab_switcher" in s:
    print("Fragment schon erledigt"); sys.exit(0)

for imp in ["import androidx.preference.TwoStatePreference;",
            "import org.chromium.base.ContextUtils;"]:
    if imp not in s:
        m = re.search(r"^import (androidx|org)\.", s, re.M)
        s = s[:m.start()] + imp + "\n" + s[m.start():]

a = "        SettingsUtils.addPreferencesFromResource(this, R.xml.appearance_preferences);"
b = a + '''

        TwoStatePreference classicSwitcher = findPreference("classic_tab_switcher");
        if (classicSwitcher != null) {
            classicSwitcher.setChecked(
                    ContextUtils.getAppSharedPreferences()
                            .getBoolean("classic_tab_switcher", true));
            classicSwitcher.setOnPreferenceChangeListener(
                    (pref, newValue) -> {
                        ContextUtils.getAppSharedPreferences()
                                .edit()
                                .putBoolean("classic_tab_switcher", (Boolean) newValue)
                                .apply();
                        return true;
                    });
        }'''

if a not in s:
    print("FEHLER: Fragment-Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok Fragment")