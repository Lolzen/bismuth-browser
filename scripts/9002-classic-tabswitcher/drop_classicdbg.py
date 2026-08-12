import re
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/src/org/"
     "chromium/chrome/browser/appearance/settings/AppearanceSettingsFragment.java")
s = open(F).read()
s = re.sub(r'^\s*Log\.i\("CLASSICDBG".*\n', '', s, flags=re.M)
s = s.replace("import android.util.Log;\n", "")
s = s.replace(
    "            boolean current =\n"
    "                    ContextUtils.getAppSharedPreferences()"
    '.getBoolean("classic_tab_switcher_v2", true);\n',
    "            boolean current =\n"
    "                    ContextUtils.getAppSharedPreferences()\n"
    '                            .getBoolean("classic_tab_switcher_v2", true);\n')
open(F, "w").write(s)
print("Logging entfernt")