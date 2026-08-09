#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
cd "$S" || exit 1

echo "=== cr_shortcut_input/BUILD.gn Kopf ==="
sed -n '1,20p' ui/webui/resources/cr_components/cr_shortcut_input/BUILD.gn

echo
echo "=== extensions-WebUI BUILD.gn um Zeile 151 ==="
sed -n '140,160p' chrome/browser/resources/extensions/BUILD.gn

echo
echo "=== ist enable_webui_ntp ein setzbares Arg? ==="
git grep -n "enable_webui_ntp" -- "*.gni" | head