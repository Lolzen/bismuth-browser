import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/android/"
     "features/tab_ui/BUILD.gn")
s = open(F).read()

if "tab_list_card_item.xml" in s:
    print("schon eingetragen")
    sys.exit(0)

anchor = '    "java/res/layout/tab_grid_card_item.xml",'
if anchor not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

add = (anchor + "\n"
       '    "java/res/layout/tab_list_card_item.xml",\n'
       '    "java/res/drawable/selected_tab_background.xml",\n'
       '    "java/res/drawable/selected_tab_background_incognito.xml",')
open(F, "w").write(s.replace(anchor, add, 1))
print("ok")