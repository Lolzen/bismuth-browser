import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/"
     "extensions/item.ts")
s = open(F).read()

a = """  private hasMv2DeprecationWarning_(): boolean {
    return this.data.disableReasons.unsupportedManifestVersion;
  }"""
b = """  private hasMv2DeprecationWarning_(): boolean {
    // Bismuth keeps Manifest V2 supported, so this warning never applies.
    // Returning false here also restores the description, which the upstream
    // code hides whenever an MV2 warning is present.
    return false;
  }"""

if "Bismuth keeps Manifest V2 supported" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")