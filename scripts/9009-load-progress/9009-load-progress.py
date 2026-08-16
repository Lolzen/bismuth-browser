import re, sys
R = "/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/resources/extensions/"

# ---------- toolbar.ts ----------
f = R + "toolbar.ts"
s = open(f).read()
if "isLoadingUnpacked_" in s:
    print("toolbar.ts schon erledigt")
else:
    imp = "import 'chrome://resources/cr_elements/cr_progress/cr_progress.js';\n"
    m = re.search(r"^import ", s, re.M)
    if not m:
        print("FEHLER: kein import in toolbar.ts"); sys.exit(1)
    s = s[:m.start()] + imp + s[m.start():]

    a = "      isUpdating_: {type: Boolean},"
    if a not in s:
        print("FEHLER: properties-Anker fehlt"); sys.exit(1)
    s = s.replace(a, a + "\n      isLoadingUnpacked_: {type: Boolean},", 1)

    a = "  accessor inDevMode: boolean = false;"
    if a not in s:
        print("FEHLER: accessor-Anker fehlt"); sys.exit(1)
    s = s.replace(a, a + "\n  protected accessor isLoadingUnpacked_: boolean = false;", 1)

    a = """  protected onLoadUnpackedClick_() {
    this.delegate.loadUnpacked()
        .then((success) => {
          if (success) {
            const toastManager = getToastManager();
            toastManager.duration = TOAST_DURATION_MS;
            toastManager.show(this.i18n('toolbarLoadUnpackedDone'));
          }
        })
        .catch(loadError => {
          this.fire('load-error', loadError);
        });"""
    b = """  protected onLoadUnpackedClick_() {
    // Unpacked extensions are copied into app storage before loading, which
    // can take a while for large extensions. Show progress until it settles.
    this.isLoadingUnpacked_ = true;
    this.delegate.loadUnpacked()
        .then((success) => {
          if (success) {
            const toastManager = getToastManager();
            toastManager.duration = TOAST_DURATION_MS;
            toastManager.show(this.i18n('toolbarLoadUnpackedDone'));
          }
        })
        .catch(loadError => {
          this.fire('load-error', loadError);
        })
        .finally(() => {
          this.isLoadingUnpacked_ = false;
        });"""
    if a not in s:
        print("FEHLER: onLoadUnpackedClick_-Anker fehlt"); sys.exit(1)
    s = s.replace(a, b, 1)
    open(f, "w").write(s)
    print("ok toolbar.ts")

# ---------- toolbar.html.ts ----------
f = R + "toolbar.html.ts"
s = open(f).read()
if "loadProgress" in s:
    print("toolbar.html.ts schon erledigt")
else:
    a = """  </div>
</div>
<!--_html_template_end_-->"""
    b = """  </div>
  ${this.isLoadingUnpacked_ ? html`
    <div id="loadProgress">
      <cr-progress indeterminate></cr-progress>
      <div id="loadProgressLabel">Copying extension into app storage...</div>
    </div>` : ''}
</div>
<!--_html_template_end_-->"""
    if a not in s:
        print("FEHLER: html-Anker fehlt"); sys.exit(1)
    open(f, "w").write(s.replace(a, b, 1))
    print("ok toolbar.html.ts")

# ---------- toolbar.css ----------
f = R + "toolbar.css"
s = open(f).read()
if "#loadProgress" in s:
    print("toolbar.css schon erledigt")
else:
    open(f, "a").write("""
#loadProgress {
  padding: 8px 0;
  width: 100%;
}

#loadProgressLabel {
  color: var(--cr-secondary-text-color);
  font-size: 12px;
  padding-top: 6px;
}
""")
    print("ok toolbar.css")