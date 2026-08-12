import base64, re, sys, urllib.request

TAG = "138.0.7204.310"
B = "https://chromium.googlesource.com/chromium/src/+/refs/tags/" + TAG + "/"
P = "chrome/android/features/tab_ui/java/res/values/dimens.xml"
D = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/java/res/values/dimens.xml")

if len(sys.argv) < 2:
    print("Aufruf: add_dimen.py name [name ...]")
    sys.exit(1)

with urllib.request.urlopen(B + P + "?format=TEXT", timeout=30) as r:
    old = base64.b64decode(r.read()).decode()

cur = open(D).read()
add = []
for n in sys.argv[1:]:
    if 'name="' + n + '"' in cur:
        print("schon da:", n)
        continue
    m = re.search(r'^\s*<dimen name="' + re.escape(n) + r'".*$', old, re.M)
    if m:
        add.append("    " + m.group(0).strip())
        print("uebernommen:", n)
    else:
        print("NICHT in 138 gefunden:", n)

if add:
    cur = cur.replace("</resources>", "\n".join(add) + "\n</resources>", 1)
    open(D, "w").write(cur)