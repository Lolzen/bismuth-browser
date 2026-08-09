import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/common/"
     "extensions/api/api_sources.gni")
s = open(F).read()

if "Desktop-Android" in s:
    print("schon gepatcht")
    sys.exit(0)

anchor = ('chrome_extensions_api_schema_sources = '
          'get_path_info(schema_sources_, "abspath")')
add = '''# Desktop-Android: MV2 extensions declaring browser_action need the
# browserAction schema at runtime, otherwise GetAPISchema() hits a FATAL in
# the renderer. The desktop-only block above is skipped there.
if (!enable_extensions) {
  uncompiled_sources_ += [
    "browser_action.json",
    "page_action.json",
  ]
}

'''

if anchor not in s:
    print("Anker nicht gefunden")
    sys.exit(1)

open(F, "w").write(s.replace(anchor, add + anchor, 1))
print("ok")