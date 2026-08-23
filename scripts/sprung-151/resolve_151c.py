import sys
F = ("/home/gee/kiwi-rebase/build/chromium/src/chrome/browser/extensions/"
     "api/developer_private/extension_info_generator.cc")
s = open(F).read()
a = """<<<<<<< ours
  // MV2 deprecation.
  ManifestV2Handler* mv2_handler = ManifestV2Handler::Get(profile);
  CHECK(mv2_handler);
  info.is_affected_by_mv2_deprecation =
      mv2_handler->IsExtensionAffected(extension);
=======
  // MV2 deprecation. Bismuth supports Manifest V2, so nothing is affected and
  // the deprecation panel stays hidden.
  info.is_affected_by_mv2_deprecation = false;
>>>>>>> theirs
"""
b = """  // MV2 deprecation. Bismuth supports Manifest V2, so nothing is affected and
  // the deprecation panel stays hidden.
  info.is_affected_by_mv2_deprecation = false;
"""
if a in s:
    open(F, "w").write(s.replace(a, b, 1))
    print("ok")
else:
    print("FEHLER: Anker fehlt"); sys.exit(1)