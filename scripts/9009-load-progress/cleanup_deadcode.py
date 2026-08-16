import re, sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# --- 1. Staging-Rest und zweiter Durchgang ---
F = B + "chrome/browser/extensions/api/developer_private/developer_private_functions.cc"
s = open(F).read()
n = 0

a = '  base::DeletePathRecursively(to.AddExtensionASCII("staging"));\n'
if a in s:
    s = s.replace(a, "", 1); n += 1
    print("Staging-Rest entfernt")

a2 = re.search(r"\n  // Top-level files can vanish[\s\S]*?\n  \}\n", s)
if a2:
    s = s[:a2.start()] + "\n" + s[a2.end():]
    n += 1
    print("zweiter Durchgang entfernt")

if n:
    open(F, "w").write(s)

# --- 2. item.ts zuruecknehmen ---
F = B + "chrome/browser/resources/extensions/item.ts"
s = open(F).read()
a3 = """  private hasMv2DeprecationWarning_(): boolean {
    // Bismuth keeps Manifest V2 supported, so this warning never applies.
    // Returning false here also restores the description, which the upstream
    // code hides whenever an MV2 warning is present.
    return false;
  }"""
b3 = """  private hasMv2DeprecationWarning_(): boolean {
    return this.data.disableReasons.unsupportedManifestVersion;
  }"""
if a3 in s:
    open(F, "w").write(s.replace(a3, b3, 1))
    print("item.ts zurueckgenommen")
else:
    print("item.ts schon im Originalzustand")