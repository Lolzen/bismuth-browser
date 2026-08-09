#!/usr/bin/env bash
S=/home/gee/kiwi-rebase/build/chromium/src
export PATH="/home/gee/kiwi-rebase/build/depot_tools:$PATH"
cd "$S" || exit 1

A=chrome/browser/media/router/BUILD.gn
B=ui/webui/resources/cr_components/cr_shortcut_input/BUILD.gn
C=ui/webui/resources/cr_components/managed_footnote/BUILD.gn

cp "$A" /tmp/mr.gn
cp "$B" /tmp/csi.gn
cp "$C" /tmp/mf.gn

git checkout HEAD -- "$A"
git checkout HEAD -- "$B"
git checkout HEAD -- "$C"

echo "=== Diff gegen HEAD (nur noch MV2 erwartet) ==="
git diff HEAD --stat

echo
echo "=== gn gen ohne die drei Fixes ==="
if gn gen out/Ext; then
  echo ">> laeuft ohne die Fixes, sie koennen weg"
else
  echo ">> Fixes werden gebraucht, werden zurueckgeholt"
  cp /tmp/mr.gn "$A"
  cp /tmp/csi.gn "$B"
  cp /tmp/mf.gn "$C"
  gn gen out/Ext
fi