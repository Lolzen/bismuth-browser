#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/scripts
cd "$S" || exit 1
mkdir -p common 9001-extensions-mv2 wip

move() {
  d="$1"; shift
  for f in "$@"; do
    [ -f "$f" ] && mv "$f" "$d/" && echo "$d/$f"
  done
}

# Einrichtung und Umgebung
move common check_disk.sh check_hostdeps.sh setup_bigdisk.sh
move common fetch_chromium.sh repair_sync.sh resume_sync.sh
move common find_target_tag.sh fetch_149_reference.sh

# Build und Diagnose, meilensteinunabhaengig
move common gen_ext.sh gen_vanilla.sh diag.sh catch_crash.sh
move common build_inventory.sh verify_base.sh show_anchor.sh
move common filter_sub.awk

# Meilenstein 9001
move 9001-extensions-mv2 check_ext_enabled.sh read_ext_buildflags.sh
move 9001-extensions-mv2 read_mv2.sh read_mv2_manager.sh
move 9001-extensions-mv2 read_stage_calc.sh verify_mv2.sh
move 9001-extensions-mv2 check_mediarouter_arg.sh show_assert2.sh
move 9001-extensions-mv2 test_without_gnfixes.sh

# LIST-Sackgasse und Gefaehrliches
move wip check_list_assets.sh check_list_mode.sh check_tabui_targets.sh
move wip diff_tabproperties.sh fetch_list_reference.sh
move wip find_list_removal.sh narrow_list_removal.sh find_pane_entry.sh
move wip inspect_tabui.sh check_actionstate.sh check_nested_types.sh
move wip start_feature.sh schleife_check_1.sh

echo
echo "=== uebrig ==="
ls -p | grep -v /