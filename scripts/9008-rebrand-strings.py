import re, sys
S = "/home/gee/kiwi-rebase/build/chromium/src/"
KEEP = ("The Chromium Authors", "chromium.org", "Chromium OS",
        "Chromium-OS", "chromium_", "Chromium Authors")

def rebrand(path):
    f = S + path
    try:
        lines = open(f, encoding="utf-8").read().split("\n")
    except FileNotFoundError:
        print("fehlt:", path); return
    out, changed, skipped = [], 0, 0
    for ln in lines:
        if "Chromium" in ln:
            if any(k in ln for k in KEEP):
                skipped += 1
            else:
                ln = ln.replace("Chromium", "Bismuth")
                changed += 1
        out.append(ln)
    open(f, "w", encoding="utf-8").write("\n".join(out))
    print(f"{path}: {changed} Zeilen geaendert, {skipped} bewusst behalten")

rebrand("chrome/app/chromium_strings.grd")
rebrand("chrome/app/settings_chromium_strings.grdp")
rebrand("components/components_chromium_strings.grd")

# BRANDING gezielt
f = S + "chrome/app/theme/chromium/BRANDING"
s = open(f).read()
for a, b in [("PRODUCT_FULLNAME=Chromium", "PRODUCT_FULLNAME=Bismuth"),
             ("PRODUCT_SHORTNAME=Chromium", "PRODUCT_SHORTNAME=Bismuth"),
             ("PRODUCT_INSTALLER_FULLNAME=Chromium Installer",
              "PRODUCT_INSTALLER_FULLNAME=Bismuth Installer"),
             ("PRODUCT_INSTALLER_SHORTNAME=Chromium Installer",
              "PRODUCT_INSTALLER_SHORTNAME=Bismuth Installer"),
             ("MAC_BUNDLE_ID=org.chromium.Chromium",
              "MAC_BUNDLE_ID=org.bismuth.Bismuth")]:
    s = s.replace(a, b)
open(f, "w").write(s)
print("BRANDING angepasst (COMPANY und COPYRIGHT bleiben bei The Chromium Authors)")