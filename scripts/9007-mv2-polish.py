import re, sys
S = "/home/gee/kiwi-rebase/build/chromium/src/"

def add_import(s, imp):
    if imp in s:
        return s
    m = re.search(r"^import (androidx|android|org)\.", s, re.M)
    return s[:m.start()] + imp + "\n" + s[m.start():]

def edit(path, old, new, label):
    f = S + path
    s = open(f).read()
    if new.strip().split("\n")[0] in s:
        print("schon erledigt:", label); return
    if old not in s:
        print("FEHLER: Anker fehlt bei", label); sys.exit(1)
    open(f, "w").write(s.replace(old, new, 1))
    print("ok", label)

# --- 1. Warnung beim Laden ---
edit("extensions/common/extension.cc",
"""    // Emit a warning for unpacked extensions on Manifest V2 warning that
    // MV2 is deprecated.
    if (type == Manifest::Type::kExtension && manifest_version == 2 &&
        Manifest::IsUnpackedLocation(location) &&
        !g_silence_deprecated_manifest_version_warnings) {
      *warning = errors::kManifestV2IsDeprecatedWarning;
    }
""",
"""    // Bismuth keeps Manifest V2 supported, so no deprecation warning here.
""",
"extension.cc")

# --- 2. Hinweis in der Erweiterungsseite ---
edit("chrome/browser/extensions/api/developer_private/extension_info_generator.cc",
"""  // MV2 deprecation.
  ManifestV2ExperimentManager* mv2_experiment_manager =
      ManifestV2ExperimentManager::Get(profile);
  CHECK(mv2_experiment_manager);
  info.is_affected_by_mv2_deprecation =
      mv2_experiment_manager->IsExtensionAffected(extension);
  info.did_acknowledge_mv2_deprecation_notice =
      mv2_experiment_manager->DidUserAcknowledgeNotice(extension.id());
""",
"""  // MV2 deprecation. Bismuth supports Manifest V2, so nothing is affected and
  // the deprecation panel stays hidden.
  info.is_affected_by_mv2_deprecation = false;
  info.did_acknowledge_mv2_deprecation_notice = false;
""",
"extension_info_generator.cc")

# --- 3. Schalter aus Darstellung entfernen ---
f = S + "chrome/android/java/res/xml/appearance_preferences.xml"
s = open(f).read()
if "classic_tab_switcher_v2" in s:
    s2 = re.sub(r'\s*<org\.chromium\.components\.browser_ui\.settings\.ChromeSwitchPreference\s*\n'
                r'(?:[^\n]*\n)*?[^\n]*classic_tab_switcher_v2(?:[^\n]*\n)*?[^\n]*/>\n',
                "\n", s, count=1)
    if s2 == s:
        print("FEHLER: XML-Block nicht entfernt"); sys.exit(1)
    open(f, "w").write(s2); print("ok appearance_preferences.xml")
else:
    print("schon erledigt: appearance_preferences.xml")

# --- 4. Schalter in Tabs-Einstellungen ---
f = S + "chrome/android/features/tab_ui/java/res/xml/tabs_settings.xml"
s = open(f).read()
if "classic_tab_switcher_v2" not in s:
    add = ('    <org.chromium.components.browser_ui.settings.ChromeSwitchPreference\n'
           '        android:key="classic_tab_switcher_v2"\n'
           '        android:persistent="false"\n'
           '        android:title="Classic tab switcher"\n'
           '        android:summary="Single overlapping column of tab cards"/>\n'
           '</PreferenceScreen>')
    open(f, "w").write(s.replace("</PreferenceScreen>", add, 1))
    print("ok tabs_settings.xml")
else:
    print("schon erledigt: tabs_settings.xml")

# --- 5. Listener aus AppearanceSettingsFragment entfernen ---
f = (S + "chrome/android/java/src/org/chromium/chrome/browser/appearance/"
     "settings/AppearanceSettingsFragment.java")
s = open(f).read()
if "classic_tab_switcher_v2" in s:
    s2 = re.sub(r"\n\s*TwoStatePreference classicPref[\s\S]*?\n        \}\n", "\n", s, count=1)
    if s2 == s:
        print("FEHLER: Fragment-Block nicht entfernt"); sys.exit(1)
    open(f, "w").write(s2); print("ok AppearanceSettingsFragment")
else:
    print("schon erledigt: AppearanceSettingsFragment")

# --- 6. Listener in TabsSettings ---
f = (S + "chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/"
     "tasks/tab_management/TabsSettings.java")
s = open(f).read()
if "classic_tab_switcher_v2" not in s:
    for imp in ["import androidx.preference.TwoStatePreference;",
                "import org.chromium.base.ContextUtils;"]:
        s = add_import(s, imp)
    a = "        configureShareTitlesAndUrlsWithOsSwitch();"
    b = a + '''

        TwoStatePreference classicPref = findPreference("classic_tab_switcher_v2");
        if (classicPref != null) {
            classicPref.setChecked(
                    ContextUtils.getAppSharedPreferences()
                            .getBoolean("classic_tab_switcher_v2", true));
            classicPref.setOnPreferenceChangeListener(
                    (pref, newValue) -> {
                        ContextUtils.getAppSharedPreferences()
                                .edit()
                                .putBoolean("classic_tab_switcher_v2", (Boolean) newValue)
                                .apply();
                        return true;
                    });
        }'''
    if a not in s:
        print("FEHLER: TabsSettings-Anker fehlt"); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1)); print("ok TabsSettings")
else:
    print("schon erledigt: TabsSettings")