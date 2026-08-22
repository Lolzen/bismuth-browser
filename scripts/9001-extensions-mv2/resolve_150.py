import sys
B = "/home/gee/kiwi-rebase/build/chromium/src/"

# --- extension_features.cc: Feature ist in 150 weg ---
F = B + "extensions/common/extension_features.cc"
s = open(F).read()
a = """<<<<<<< ours
=======
BASE_FEATURE(kExtensionManifestV2Disabled, base::FEATURE_DISABLED_BY_DEFAULT);

>>>>>>> theirs
"""
if a in s:
    open(F, "w").write(s.replace(a, "", 1))
    print("ok extension_features.cc")
else:
    print("FEHLER: Anker 1 fehlt")
    sys.exit(1)

# --- extension_info_generator.cc: Feld existiert nicht mehr ---
F = B + "chrome/browser/extensions/api/developer_private/extension_info_generator.cc"
s = open(F).read()
a2 = """<<<<<<< ours
  // MV2 deprecation.
  ManifestV2ExperimentManager* mv2_experiment_manager =
      ManifestV2ExperimentManager::Get(profile);
  CHECK(mv2_experiment_manager);
  info.is_affected_by_mv2_deprecation =
      mv2_experiment_manager->IsExtensionAffected(extension);
=======
  // MV2 deprecation. Bismuth supports Manifest V2, so nothing is affected and
  // the deprecation panel stays hidden.
  info.is_affected_by_mv2_deprecation = false;
  info.did_acknowledge_mv2_deprecation_notice = false;
>>>>>>> theirs
"""
b2 = """  // MV2 deprecation. Bismuth supports Manifest V2, so nothing is affected and
  // the deprecation panel stays hidden.
  info.is_affected_by_mv2_deprecation = false;
"""
if a2 in s:
    open(F, "w").write(s.replace(a2, b2, 1))
    print("ok extension_info_generator.cc")
else:
    print("FEHLER: Anker 2 fehlt")
    sys.exit(1)