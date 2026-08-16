import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/"
     "extensions/manager.css")
s = open(F).read()

rule = """
#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 13px;
  padding-top: 12px;
}
"""
n = s.count(rule)
print("gefunden:", n)
if n < 2:
    print("nichts zu tun"); sys.exit(0)

open(F, "w").write(s.replace(rule, "", 1))
print("erste Dublette entfernt")