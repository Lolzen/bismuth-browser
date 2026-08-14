S = "/home/gee/kiwi-rebase/build/chromium/src/"
for p in ["chrome/app/chromium_strings.grd",
          "chrome/app/settings_chromium_strings.grdp",
          "components/components_chromium_strings.grd"]:
    f = S + p
    s = open(f, encoding="utf-8").read()
    n = s.count("BismuthOS")
    if n:
        open(f, "w", encoding="utf-8").write(s.replace("BismuthOS", "ChromiumOS"))
    print(p, "->", n, "zurueckgesetzt")