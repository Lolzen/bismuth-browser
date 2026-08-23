import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# --- chrome_feature_list.cc: nur unsere Zeile, ohne Nachbarn aus 150 ---
F = B + "chrome/browser/flags/android/chrome_feature_list.cc"
s = open(F).read()
a = """<<<<<<< ours
BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_DISABLED_BY_DEFAULT);
=======
BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_ENABLED_BY_DEFAULT);
BASE_FEATURE(kSuppressToolbarCapturesAtGestureEnd, base::FEATURE_ENABLED_BY_DEFAULT);
>>>>>>> theirs
"""
b = "BASE_FEATURE(kSubmenusInAppMenu, base::FEATURE_ENABLED_BY_DEFAULT);\n"
if a in s:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok chrome_feature_list.cc")
else:
    print("FEHLER: Anker feature_list fehlt")

# --- manager.css: beide Seiten behalten ---
F = B + "chrome/browser/resources/extensions/manager.css"
s = open(F).read()
pat = re.compile(r"<<<<<<< ours\n(.*?)=======\n(.*?)>>>>>>> theirs\n", re.S)
n = len(pat.findall(s))
if n:
    open(F, "w").write(pat.sub(lambda m: m.group(1) + m.group(2), s))
    print("ok manager.css -", n, "Konflikt(e) zusammengefuehrt")
else:
    print("manager.css: kein Konflikt gefunden")