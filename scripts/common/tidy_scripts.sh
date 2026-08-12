#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/scripts
mkdir -p "$S/wip"

for f in check_list_deps.sh fetch_tablistview.sh probe_listmode_apis.sh \
         add_listmode_files.py add_listmode_sources.py add_listmode_res.py \
         fix_listmode.py revert_listmode.sh wire_listmode_hook_test.py \
         wire_listmode_1.py wire_listmode_2.py wire_listmode_3.py \
         wire_listmode_4.py wire_listmode_5.py wire_listmode_6.py \
         wire_listmode_7.py classic_pref.py classic_pref_ui.py \
         classic_pref_fix.py patch_copyload.py patch_header.py \
         copyload_log.py; do
  [ -f "$S/$f" ] && mv "$S/$f" "$S/wip/" && echo "-> wip/$f"
done

echo
echo "=== aktiv ==="
ls "$S" | grep -v '^wip$'