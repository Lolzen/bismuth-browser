import sys
F = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/BUILD.gn"
s = open(F).read()

a = """  if (enable_dice_support) {
    public_deps += [
      "//chrome/browser/profiles/batch_upload",
      "//chrome/browser/profiles/batch_upload:impl",
    ]
    if (!is_android) {
      deps += [ "//chrome/browser/ui/webui/signin/signout_confirmation" ]
    }
  }"""

b = """  if (enable_dice_support && !is_android) {
    public_deps += [
      "//chrome/browser/profiles/batch_upload",
      "//chrome/browser/profiles/batch_upload:impl",
    ]
    deps += [ "//chrome/browser/ui/webui/signin/signout_confirmation" ]
  }"""

if "enable_dice_support && !is_android" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")