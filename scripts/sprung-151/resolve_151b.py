import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

F = B + "extensions/common/extension.cc"
s = open(F).read()
a = """<<<<<<< ours
    // Emit a warning for unpacked extensions on Manifest V2 warning that
    // MV2 is deprecated.
    if (type == Manifest::Type::kExtension && manifest_version == 2 &&
        Manifest::IsUnpackedLocation(location)) {
      *warning = errors::kManifestV2IsDeprecatedWarning;
    }
=======
    // Bismuth keeps Manifest V2 supported, so no deprecation warning here.
>>>>>>> theirs
"""
b = "    // Bismuth keeps Manifest V2 supported, so no deprecation warning here.\n"
if a in s:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok extension.cc")
else:
    print("FEHLER: Anker extension.cc")

F = (B + "chrome/android/java/src/org/chromium/chrome/browser/"
     "tabbed_mode/TabbedAppMenuPropertiesDelegate.java")
s = open(F).read()
a2 = """<<<<<<< ours
        submenuItems.add(buildExtensionsMenuItem(/* showIcon= */ false));
=======
        // Opens the toolbar's puzzle-icon menu, which only exists on
        // tablet-sized layouts. Omitted here.
        // submenuItems.add(buildExtensionsMenuItem());
>>>>>>> theirs
"""
b2 = """        // Opens the toolbar's puzzle-icon menu, which only exists on
        // tablet-sized layouts. Omitted here.
        // submenuItems.add(buildExtensionsMenuItem(/* showIcon= */ false));
"""
if a2 in s:
    open(F, "w").write(s.replace(a2, b2, 1))
    print("ok TabbedAppMenuPropertiesDelegate.java")
else:
    print("FEHLER: Anker Java")