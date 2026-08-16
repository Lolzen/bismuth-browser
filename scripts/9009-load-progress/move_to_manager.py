import re, sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

def edit(fn, pairs, label):
    f = R + fn
    s = open(f).read()
    for a, b in pairs:
        if a not in s:
            print("FEHLER in", label, "->", a.strip().split("\n")[0][:50])
            sys.exit(1)
        s = s.replace(a, b, 1)
    open(f, "w").write(s)
    print("ok", label)

# ---------- toolbar.ts ----------
f = R + "toolbar.ts"
s = open(f).read()
if "isLoadingUnpacked_" in s:
    s = s.replace("import 'chrome://resources/cr_elements/cr_dialog/cr_dialog.js';\n", "")
    s = s.replace("import 'chrome://resources/cr_elements/cr_progress/cr_progress.js';\n", "")
    s = s.replace("\n      isLoadingUnpacked_: {type: Boolean},", "")
    s = s.replace("\n  protected accessor isLoadingUnpacked_: boolean = false;", "")
    s = s.replace("    this.isLoadingUnpacked_ = true;",
                  "    this.fire('load-progress', true);")
    s = s.replace("          this.isLoadingUnpacked_ = false;",
                  "          this.fire('load-progress', false);")
    open(f, "w").write(s)
    print("ok toolbar.ts")
else:
    print("toolbar.ts schon erledigt")

# ---------- toolbar.html.ts ----------
f = R + "toolbar.html.ts"
s = open(f).read()
if "loadProgressDialog" in s:
    s = re.sub(r"\n\$\{this\.isLoadingUnpacked_ \? html`[\s\S]*?</cr-dialog>` : ''\}", "", s, count=1)
    open(f, "w").write(s)
    print("ok toolbar.html.ts")
else:
    print("toolbar.html.ts schon erledigt")

# ---------- toolbar.css ----------
f = R + "toolbar.css"
s = open(f).read()
s2 = re.sub(r"\n#loadProgressLabel \{[\s\S]*?\n\}\n", "", s, count=1)
open(f, "w").write(s2)
print("ok toolbar.css" if s2 != s else "toolbar.css schon erledigt")

# ---------- manager.ts ----------
f = R + "manager.ts"
s = open(f).read()
if "showLoadProgressDialog_" not in s:
    m = re.search(r"^import ", s, re.M)
    s = (s[:m.start()]
         + "import 'chrome://resources/cr_elements/cr_dialog/cr_dialog.js';\n"
         + "import 'chrome://resources/cr_elements/cr_progress/cr_progress.js';\n"
         + s[m.start():])
    s = s.replace(
        "    'load-error': CustomEvent<Error|chrome.developerPrivate.LoadError>;",
        "    'load-error': CustomEvent<Error|chrome.developerPrivate.LoadError>;\n"
        "    'load-progress': CustomEvent<boolean>;", 1)
    s = s.replace("      showLoadErrorDialog_: {type: Boolean},",
                  "      showLoadErrorDialog_: {type: Boolean},\n"
                  "      showLoadProgressDialog_: {type: Boolean},", 1)
    s = s.replace("  protected accessor showLoadErrorDialog_: boolean = false;",
                  "  protected accessor showLoadErrorDialog_: boolean = false;\n"
                  "  protected accessor showLoadProgressDialog_: boolean = false;", 1)
    s = s.replace("    this.addEventListener('load-error', this.onLoadError_);",
                  "    this.addEventListener('load-error', this.onLoadError_);\n"
                  "    this.addEventListener('load-progress', this.onLoadProgress_);", 1)
    s = s.replace("    this.showLoadErrorDialog_ = false;\n  }",
                  "    this.showLoadErrorDialog_ = false;\n  }\n\n"
                  "  private onLoadProgress_(e: CustomEvent<boolean>) {\n"
                  "    this.showLoadProgressDialog_ = e.detail;\n  }", 1)
    open(f, "w").write(s)
    print("ok manager.ts")
else:
    print("manager.ts schon erledigt")

# ---------- manager.html.ts ----------
f = R + "manager.html.ts"
s = open(f).read()
a = """  </extensions-load-error>`: ''}"""
b = """  </extensions-load-error>`: ''}
${this.showLoadProgressDialog_ ? html`
  <cr-dialog id="load-progress" show-on-attach>
    <div slot="title">Loading extension</div>
    <div slot="body">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>
  </cr-dialog>`: ''}"""
if "showLoadProgressDialog_" in s:
    print("manager.html.ts schon erledigt")
else:
    edit("manager.html.ts", [(a, b)], "manager.html.ts")

# ---------- manager.css ----------
f = R + "manager.css"
s = open(f).read()
if "#loadProgressLabel" not in s:
    open(f, "a").write("""
#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 13px;
  padding-top: 12px;
}
""")
    print("ok manager.css")
else:
    print("manager.css schon erledigt")