import re, sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

# ---------- service.ts ----------
f = R + "service.ts"
s = open(f).read()
if "getCopyProgressTarget" in s:
    print("service.ts schon erledigt")
else:
    a = """  getItemStateChangedTarget() {
    return chrome.developerPrivate.onItemStateChanged;
  }"""
    b = a + """

  getCopyProgressTarget() {
    return chrome.developerPrivate.onCopyProgress;
  }"""
    if a not in s:
        print("FEHLER: service.ts-Anker"); sys.exit(1)
    s = s.replace(a, b, 1)
    m = re.search(r"^\s*getItemStateChangedTarget\(\):.*;$", s, re.M)
    if m:
        s = s[:m.end()] + "\n  getCopyProgressTarget(): ChromeEvent<" \
            "(progress: chrome.developerPrivate.CopyProgress) => void>;" + s[m.end():]
        print("  Schnittstelle mit ergaenzt")
    open(f, "w").write(s)
    print("ok service.ts")

# ---------- manager.ts ----------
f = R + "manager.ts"
s = open(f).read()
if "loadProgressTotal_" in s:
    print("manager.ts schon erledigt")
else:
    pairs = [
      ("      showLoadProgressDialog_: {type: Boolean},",
       "      showLoadProgressDialog_: {type: Boolean},\n"
       "      loadProgressCopied_: {type: Number},\n"
       "      loadProgressTotal_: {type: Number},"),
      ("  protected accessor showLoadProgressDialog_: boolean = false;",
       "  protected accessor showLoadProgressDialog_: boolean = false;\n"
       "  protected accessor loadProgressCopied_: number = 0;\n"
       "  protected accessor loadProgressTotal_: number = 0;"),
      ("      service.getItemStateChangedTarget().addListener(\n"
       "          this.onItemStateChanged_.bind(this));",
       "      service.getItemStateChangedTarget().addListener(\n"
       "          this.onItemStateChanged_.bind(this));\n"
       "      service.getCopyProgressTarget().addListener(\n"
       "          this.onCopyProgress_.bind(this));"),
      ("  private onLoadProgress_(e: CustomEvent<boolean>) {\n"
       "    this.showLoadProgressDialog_ = e.detail;",
       "  private onCopyProgress_(\n"
       "      progress: chrome.developerPrivate.CopyProgress) {\n"
       "    this.loadProgressCopied_ = progress.copied;\n"
       "    this.loadProgressTotal_ = progress.total;\n"
       "  }\n\n"
       "  private onLoadProgress_(e: CustomEvent<boolean>) {\n"
       "    this.showLoadProgressDialog_ = e.detail;\n"
       "    this.loadProgressCopied_ = 0;\n"
       "    this.loadProgressTotal_ = 0;"),
    ]
    for a, b in pairs:
        if a not in s:
            print("FEHLER manager.ts:", a.strip()[:45]); sys.exit(1)
        s = s.replace(a, b, 1)
    open(f, "w").write(s)
    print("ok manager.ts")

# ---------- manager.html.ts ----------
f = R + "manager.html.ts"
s = open(f).read()
if "loadProgressTotal_" in s:
    print("manager.html.ts schon erledigt")
else:
    a = """      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>"""
    b = """      <cr-progress ?indeterminate="${!this.loadProgressTotal_}"
          .value="${this.loadProgressCopied_}"
          .max="${this.loadProgressTotal_ || 1}"></cr-progress>
      <div id="loadProgressLabel">${this.loadProgressTotal_ ?
          `Copying ${this.loadProgressCopied_} of ${this.loadProgressTotal_} files` :
          'Preparing to copy...'}</div>"""
    if a not in s:
        print("FEHLER: html-Anker"); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1))
    print("ok manager.html.ts")