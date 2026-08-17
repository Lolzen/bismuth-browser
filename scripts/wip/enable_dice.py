import sys
F = "/home/gee/kiwi-rebase/build/chromium/src/components/signin/features.gni"
s = open(F).read()

if "is_desktop_android" in s:
    print("schon erledigt"); sys.exit(0)

pairs = [
("enable_dice_support = is_linux || is_mac || is_win || is_fuchsia",
 "enable_dice_support =\n"
 "    is_linux || is_mac || is_win || is_fuchsia || is_desktop_android"),
("enable_mirror = is_android || is_chromeos || is_ios",
 "enable_mirror = (is_android && !is_desktop_android) || is_chromeos || is_ios"),
]

for a, b in pairs:
    if a not in s:
        print("FEHLER: Anker fehlt ->", a[:45]); sys.exit(1)
    s = s.replace(a, b, 1)

open(F, "w").write(s)
print("ok")
