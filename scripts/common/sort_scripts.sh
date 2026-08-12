#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/scripts
cd "$S" || exit 1

mkdir -p common 9001-extensions-mv2 9002-classic-tabswitcher
mkdir -p 9003-copy-on-load 9004-webstore-desktop wip

move() {
  d="$1"; shift
  for f in "$@"; do
    [ -f "$f" ] && mv "$f" "$d/" && echo "$d/$f"
  done
}

move common patch_extract.sh sanity_check.sh verify_tree.sh
move common secure_vanilla.sh build_worklist.sh make_patch.sh
move common archive_apk.sh add_dimen.py gen_ext2.sh count_gates.sh
move common inspect_desktop_android.sh measure_mv2_removal.sh
move common tidy_scripts.sh sort_scripts.sh

move 9001-extensions-mv2 find_mv2.sh patch_mv2.sh verify_mv2.sh
move 9001-extensions-mv2 fix_mediarouter.sh fix_webui_asserts.sh
move 9001-extensions-mv2 fix_cr_elements.sh fix_shortcut_input.sh
move 9001-extensions-mv2 patch_saf_enum.sh patch_saf_recurse.sh
move 9001-extensions-mv2 patch_browseraction_schema.py
move 9001-extensions-mv2 make_mv2_probes.sh make_probe_c.sh
move 9001-extensions-mv2 catch_ext_error.sh probe_listmode_apis.sh

move 9002-classic-tabswitcher classic_switcher.py switcher_toggle.py
move 9002-classic-tabswitcher drop_classicdbg.py

move 9003-copy-on-load copyload2.py copyload_atomic.py
move 9003-copy-on-load copyload_moredbg.py

move 9004-webstore-desktop webstore_exception.py

move wip patch_l10n.sh webstore_desktop.py webstore_wire.py
move wip webstore_ua.py webstore_ua_dbg.py

echo
echo "=== uebrig im Wurzelverzeichnis ==="
ls -p | grep -v /