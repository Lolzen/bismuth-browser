import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/"
     "extensions/item.ts")
s = open(F).read()

if "getCopyProgressTarget" in s:
    print("schon erledigt"); sys.exit(0)

a = """  getItemStateChangedTarget():
      ChromeEvent<(data: chrome.developerPrivate.EventData) => void>;"""
b = a + """
  getCopyProgressTarget():
      ChromeEvent<(progress: chrome.developerPrivate.CopyProgress) => void>;"""
if a not in s:
    print("FEHLER: Anker 1 fehlt"); sys.exit(1)
s = s.replace(a, b, 1)

a2 = """  getItemStateChangedTarget() {
    return new FakeChromeEvent();
  }"""
b2 = a2 + """

  getCopyProgressTarget() {
    return new FakeChromeEvent();
  }"""
if a2 not in s:
    print("FEHLER: Anker 2 fehlt"); sys.exit(1)
s = s.replace(a2, b2, 1)

open(F, "w").write(s)
print("ok")