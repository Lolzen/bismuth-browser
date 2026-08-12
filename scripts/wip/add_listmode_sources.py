import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/features/"
     "tab_ui/tab_management_java_sources.gni")
P = "//chrome/android/features/tab_ui/java/src/org/chromium/chrome/browser/tasks/tab_management/"

s = open(F).read()
if "TabListViewBinder.java" in s:
    print("schon eingetragen")
    sys.exit(0)

anchor = '  "' + P + 'TabStripViewBinder.java",'
if anchor not in s:
    print("Anker nicht gefunden - Einrueckung pruefen")
    sys.exit(1)

add = (anchor + "\n"
       '  "' + P + 'TabListView.java",\n'
       '  "' + P + 'TabListViewBinder.java",')
open(F, "w").write(s.replace(anchor, add, 1))
print("ok")