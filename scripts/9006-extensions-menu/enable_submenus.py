import sys
S = "/home/gee/kiwi-rebase/build/chromium/src/"

# 1. Untermenues standardmaessig an
F = S + "chrome/browser/flags/android/chrome_feature_list.cc"
s = open(F).read()
a = "BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_DISABLED_BY_DEFAULT);"
b = "BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_ENABLED_BY_DEFAULT);"
if b in s:
    print("Feature schon aktiviert")
elif a not in s:
    print("FEHLER: Feature-Anker fehlt"); sys.exit(1)
else:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok Feature")

# 2. wirkungslosen Eintrag aus dem Untermenue nehmen
F = (S + "chrome/android/java/src/org/chromium/chrome/browser/tabbed_mode/"
     "TabbedAppMenuPropertiesDelegate.java")
s = open(F).read()
a2 = "        submenuItems.add(buildExtensionsMenuItem());\n"
b2 = ("        // Opens the toolbar's puzzle-icon menu, which only exists on\n"
      "        // tablet-sized layouts. Omitted here.\n"
      "        // submenuItems.add(buildExtensionsMenuItem());\n")
if "puzzle-icon menu, which only exists" in s:
    print("Eintrag schon entfernt")
elif a2 not in s:
    print("FEHLER: Menue-Anker fehlt"); sys.exit(1)
else:
    open(F, "w").write(s.replace(a2, b2, 1))
    print("ok Menue")