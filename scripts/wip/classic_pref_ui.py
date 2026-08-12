import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/java/res/"
     "xml/appearance_preferences.xml")
s = open(F).read()

if "classic_tab_switcher" in s:
    print("schon eingetragen")
    sys.exit(0)

anchor = "</PreferenceScreen>"
add = '''    <org.chromium.components.browser_ui.settings.ChromeSwitchPreference
        android:key="classic_tab_switcher"
        android:order="3"
        android:defaultValue="true"
        android:title="Classic tab switcher"
        android:summary="Show tabs as a single overlapping column" />
</PreferenceScreen>'''

if anchor not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

open(F, "w").write(s.replace(anchor, add, 1))
print("ok")