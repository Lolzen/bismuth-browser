import re, sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

# ---------- toolbar.ts: Dialog-Import ----------
f = R + "toolbar.ts"
s = open(f).read()
imp = "import 'chrome://resources/cr_elements/cr_dialog/cr_dialog.js';\n"
if imp not in s:
    m = re.search(r"^import ", s, re.M)
    s = s[:m.start()] + imp + s[m.start():]
    open(f, "w").write(s)
    print("ok toolbar.ts")
else:
    print("toolbar.ts schon erledigt")

# ---------- toolbar.html.ts: Overlay -> cr-dialog ----------
f = R + "toolbar.html.ts"
s = open(f).read()
a = """${this.isLoadingUnpacked_ ? html`
  <div id="loadProgressOverlay">
    <div id="loadProgressCard">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </div>` : ''}"""
b = """${this.isLoadingUnpacked_ ? html`
  <cr-dialog id="loadProgressDialog" show-on-attach>
    <div slot="title">Loading extension</div>
    <div slot="body">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </cr-dialog>` : ''}"""
if "loadProgressDialog" in s:
    print("html schon erledigt")
elif a not in s:
    print("FEHLER: html-Anker fehlt"); sys.exit(1)
else:
    open(f, "w").write(s.replace(a, b, 1))
    print("ok toolbar.html.ts")

# ---------- toolbar.css: Overlay-Regeln raus ----------
f = R + "toolbar.css"
s = open(f).read()
alt = """
#loadProgressOverlay {
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  inset: 0;
  justify-content: center;
  position: fixed;
  z-index: 100;
}

#loadProgressCard {
  background: var(--cr-card-background-color, #202124);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  min-width: 240px;
  padding: 20px 24px;
}

#loadProgressLabel {
  color: var(--cr-primary-text-color);
  font-size: 13px;
  padding-top: 12px;
  text-align: center;
}
"""
neu = """
#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 13px;
  padding-top: 12px;
}
"""
if "#loadProgressOverlay" not in s:
    print("css schon erledigt")
else:
    open(f, "w").write(s.replace(alt, neu, 1))
    print("ok toolbar.css")