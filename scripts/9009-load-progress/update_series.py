F = "/home/gee/kiwi-rebase/scripts/common/split_patches.sh"
s = open(F).read()

a = """mk 9009-load-progress \\
  chrome/browser/resources/extensions/toolbar.ts \\
  chrome/browser/resources/extensions/toolbar.html.ts \\
  chrome/browser/resources/extensions/toolbar.css"""

b = """mk 9009-load-progress \\
  chrome/browser/resources/extensions \\
  chrome/common/extensions/api/developer_private.webidl \\
  tools/typescript/definitions/developer_private.d.ts"""

if b in s:
    print("schon erledigt")
elif a not in s:
    print("FEHLER: Anker fehlt")
else:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok")