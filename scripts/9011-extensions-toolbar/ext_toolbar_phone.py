import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# --- 1. ViewStub in die Telefon-Symbolleiste ---
F = B + "chrome/browser/ui/android/toolbar/java/res/layout/toolbar_phone.xml"
s = open(F).read()
a = """        <org.chromium.chrome.browser.toolbar.top.ToggleTabStackButton"""
b = """        <ViewStub
            android:id="@+id/extensions_toolbar_container_stub"
            android:inflatedId="@+id/extensions_toolbar_container"
            android:layout_width="wrap_content"
            android:layout_height="match_parent"
            android:layout_gravity="top"/>
        <org.chromium.chrome.browser.toolbar.top.ToggleTabStackButton"""
if "extensions_toolbar_container_stub" in s:
    print("xml schon erledigt")
elif a not in s:
    print("FEHLER: xml-Anker fehlt"); sys.exit(1)
else:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok toolbar_phone.xml")

# --- 2. ueberfluessige Typumwandlung entfernen ---
F = B + "chrome/android/java/src/org/chromium/chrome/browser/toolbar/ToolbarManager.java"
s = open(F).read()
a2 = "                                                        (ToolbarTablet) mToolbarLayout,"
b2 = "                                                        mToolbarLayout,"
if b2 in s:
    print("java schon erledigt")
elif a2 not in s:
    print("FEHLER: java-Anker fehlt - bitte grep zeigen"); sys.exit(1)
else:
    open(F, "w").write(s.replace(a2, b2, 1))
    print("ok ToolbarManager.java")