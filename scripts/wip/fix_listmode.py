import re, subprocess, sys, base64, urllib.request

S = "/home/gee/kiwi-rebase/build/chromium/src"
T = (S + "/chrome/android/features/tab_ui/java/src/org/chromium/"
     "chrome/browser/tasks/tab_management/")
RES = S + "/chrome/android/features/tab_ui/java/res/"
TAG = "138.0.7204.310"
B = "https://chromium.googlesource.com/chromium/src/+/refs/tags/" + TAG + "/"

def fetch(p):
    try:
        with urllib.request.urlopen(B + p + "?format=TEXT", timeout=30) as r:
            return base64.b64decode(r.read()).decode()
    except Exception as e:
        print("FEHLER beim Holen von", p, e)
        return None

# --- 1. Java: Theme-Aufrufe anpassen ---
f = T + "TabListViewBinder.java"
s = open(f).read()

s = s.replace("TabUiThemeProvider.getActionButtonTintList",
              "TabCardThemeUtil.getActionButtonTintList")

# vierten Parameter ergaenzen: schliessende Klammer des Aufrufs finden
for m in ["getActionButtonTintList", "getCardViewBackgroundColor",
          "getTitleTextColor", "getMiniThumbnailPlaceholderColor"]:
    pat = re.compile(
        r"(TabCardThemeUtil\." + m + r"\((?:[^()]|\([^()]*\))*?)\)",
        re.S)
    def repl(mo):
        inner = mo.group(1)
        if inner.rstrip().endswith("null"):
            return mo.group(0)
        return inner + ", /* tabGroupCardColor= */ null)"
    s = pat.sub(repl, s, count=0)

if "import org.chromium.components.browser_ui.util.TextResolver;" not in s:
    s = s.replace("import org.chromium.ui.modelutil.PropertyKey;",
                  "import org.chromium.components.browser_ui.util.TextResolver;\n"
                  "import org.chromium.ui.modelutil.PropertyKey;")
open(f, "w").write(s)
print("Java angepasst")

# --- 2. Layout: fehlende IDs als leere Container ---
lay = RES + "layout/tab_list_card_item.xml"
x = open(lay).read()
if "after_title_container" not in x:
    stub = ('        <include layout="@layout/modern_list_item_view" />\n'
            '        <FrameLayout\n'
            '            android:id="@+id/after_title_container"\n'
            '            android:layout_width="wrap_content"\n'
            '            android:layout_height="wrap_content" />\n'
            '        <FrameLayout\n'
            '            android:id="@+id/before_description_container"\n'
            '            android:layout_width="wrap_content"\n'
            '            android:layout_height="wrap_content" />\n')
    x = x.replace('        <include layout="@layout/modern_list_item_view" />\n',
                  stub, 1)
    open(lay, "w").write(x)
    print("Layout ergaenzt")

# --- 3. dimens aus 138 nachziehen ---
need = ["selection_tab_list_toggle_button_lateral_inset",
        "selection_tab_list_toggle_button_vertical_inset",
        "tab_list_selected_inset_low_end",
        "tab_card_label_list_margin_end"]
old = fetch("chrome/android/features/tab_ui/java/res/values/dimens.xml")
if old:
    lines = []
    for n in need:
        m = re.search(r'^\s*<dimen name="' + n + r'".*$', old, re.M)
        if m:
            lines.append("    " + m.group(0).strip())
        else:
            print("nicht gefunden in 138:", n)
    d = RES + "values/dimens.xml"
    cur = open(d).read()
    add = [l for l in lines if l.strip() not in cur]
    if add:
        cur = cur.replace("</resources>", "\n".join(add) + "\n</resources>", 1)
        open(d, "w").write(cur)
        print("dimens ergaenzt:", len(add))

# --- 4. drawables aus 138 ---
for n in ["selected_tab_background", "selected_tab_background_incognito"]:
    p = "chrome/android/features/tab_ui/java/res/drawable/" + n + ".xml"
    c = fetch(p)
    if c:
        open(RES + "drawable/" + n + ".xml", "w").write(c)
        print("drawable gesetzt:", n)