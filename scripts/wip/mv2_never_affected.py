import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/extensions/browser/"
     "mv2_deprecation_impact_checker.cc")
s = open(F).read()

a = """    const HashedExtensionId& hashed_id) {
  // Only extensions < MV3."""
b = """    const HashedExtensionId& hashed_id) {
  // Bismuth keeps Manifest V2 supported, so no extension is ever affected by
  // the deprecation. Intervening here instead of at the feature flags makes
  // this independent of flag expiry, which silently reset our patches in 150.
  return false;

  // Only extensions < MV3."""

if "Bismuth keeps Manifest V2 supported" in s:
    print("schon erledigt"); sys.exit(0)
if a not in s:
    print("FEHLER: Anker fehlt"); sys.exit(1)
open(F, "w").write(s.replace(a, b, 1))
print("ok")