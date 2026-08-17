import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# 1. Kern von DICE behalten, nur batch_upload herausnehmen
F = B + "chrome/browser/signin/BUILD.gn"
s = open(F).read()
a = """      "//chrome/browser/profiles/batch_upload",
      "//chrome/browser/profiles/batch_upload:impl",
"""
if a in s:
    open(F, "w").write(s.replace(a, "", 1))
    print("ok signin/BUILD.gn")
else:
    print("signin/BUILD.gn schon erledigt oder Anker fehlt")

# 2. Block ganz ausklammern
F = B + "chrome/browser/ui/profiles/BUILD.gn"
s = open(F).read()
a2 = """    if (enable_dice_support) {
      sources += [
        "batch_upload_ui_delegate.h","""
b2 = """    if (enable_dice_support && !is_android) {
      sources += [
        "batch_upload_ui_delegate.h","""
if b2.split("\n")[0] in s:
    print("ui/profiles schon erledigt")
elif a2 not in s:
    print("FEHLER: ui/profiles-Anker fehlt"); sys.exit(1)
else:
    open(F, "w").write(s.replace(a2, b2, 1))
    print("ok ui/profiles/BUILD.gn")