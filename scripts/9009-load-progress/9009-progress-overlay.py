import sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

# ---------- toolbar.html.ts: aus dem Drawer heraus, als Overlay ----------
f = R + "toolbar.html.ts"
s = open(f).read()
if "loadProgressOverlay" in s:
    print("html schon erledigt")
else:
    a = """  </div>
  ${this.isLoadingUnpacked_ ? html`
    <div id="loadProgress">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>` : ''}
</div>
<!--_html_template_end_-->"""
    b = """  </div>
</div>
${this.isLoadingUnpacked_ ? html`
  <div id="loadProgressOverlay">
    <div id="loadProgressCard">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </div>` : ''}
<!--_html_template_end_-->"""
    if a not in s:
        print("FEHLER: html-Anker fehlt"); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1))
    print("ok toolbar.html.ts")

# ---------- toolbar.css ----------
f = R + "toolbar.css"
s = open(f).read()
alt = """
#loadProgress {
  padding: 8px 0;
  width: 100%;
}

#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 12px;
  padding-top: 6px;
}
"""
neu = """
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
if "#loadProgressOverlay" in s:
    print("css schon erledigt")
elif alt not in s:
    print("FEHLER: css-Anker fehlt"); sys.exit(1)
else:
    open(f, "w").write(s.replace(alt, neu, 1))
    print("ok toolbar.css")