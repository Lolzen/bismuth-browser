import re, sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

# ---------- manager.html.ts: cr-dialog -> eigenes Overlay ----------
f = R + "manager.html.ts"
s = open(f).read()
a = """${this.showLoadProgressDialog_ ? html`
  <cr-dialog id="load-progress" show-on-attach>
    <div slot="title">Loading extension</div>
    <div slot="body">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </cr-dialog>`: ''}"""
b = """${this.showLoadProgressDialog_ ? html`
  <div id="loadProgressOverlay">
    <div id="loadProgressCard">
      <div id="loadProgressTitle">Loading extension</div>
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </div>`: ''}"""
if "loadProgressOverlay" in s:
    print("html schon erledigt")
elif a not in s:
    print("FEHLER: html-Anker fehlt"); sys.exit(1)
else:
    open(f, "w").write(s.replace(a, b, 1)); print("ok manager.html.ts")

# ---------- manager.ts: Positionierung ----------
f = R + "manager.ts"
s = open(f).read()
a = """  private onLoadProgress_(e: CustomEvent<boolean>) {
    this.showLoadProgressDialog_ = e.detail;
  }"""
b = """  private positionLoadProgressBound_ = () => this.positionLoadProgress_();

  // A <dialog> centers itself in the layout viewport. On a phone the page is
  // wider than the screen, so that lands outside what the user can see. Track
  // the visual viewport instead and cover exactly the visible area.
  private positionLoadProgress_() {
    const overlay =
        this.shadowRoot.querySelector<HTMLElement>('#loadProgressOverlay');
    const viewport = window.visualViewport;
    if (!overlay || !viewport) {
      return;
    }
    overlay.style.left = `${viewport.offsetLeft}px`;
    overlay.style.top = `${viewport.offsetTop}px`;
    overlay.style.width = `${viewport.width}px`;
    overlay.style.height = `${viewport.height}px`;
  }

  private onLoadProgress_(e: CustomEvent<boolean>) {
    this.showLoadProgressDialog_ = e.detail;
    const viewport = window.visualViewport;
    if (!viewport) {
      return;
    }
    if (e.detail) {
      setTimeout(() => this.positionLoadProgress_());
      viewport.addEventListener('resize', this.positionLoadProgressBound_);
      viewport.addEventListener('scroll', this.positionLoadProgressBound_);
    } else {
      viewport.removeEventListener('resize', this.positionLoadProgressBound_);
      viewport.removeEventListener('scroll', this.positionLoadProgressBound_);
    }
  }"""
if "positionLoadProgress_" in s:
    print("manager.ts schon erledigt")
elif a not in s:
    print("FEHLER: manager.ts-Anker fehlt"); sys.exit(1)
else:
    s = s.replace(a, b, 1)
    s = s.replace("import 'chrome://resources/cr_elements/cr_dialog/cr_dialog.js';\n", "")
    open(f, "w").write(s); print("ok manager.ts")

# ---------- manager.css ----------
f = R + "manager.css"
s = open(f).read()
if "#loadProgressOverlay" in s:
    print("css schon erledigt")
else:
    open(f, "a").write("""
#loadProgressOverlay {
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  position: fixed;
  z-index: 100;
}

#loadProgressCard {
  background: var(--cr-dialog-background-color, #202124);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  max-width: 80%;
  min-width: 220px;
  padding: 20px 24px;
}

#loadProgressTitle {
  color: var(--cr-primary-text-color);
  font-size: 15px;
  padding-bottom: 14px;
}

#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 13px;
  padding-top: 12px;
}
""")
    print("ok manager.css")