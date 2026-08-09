#!/usr/bin/env bash
set -e
D=/home/gee/kiwi-rebase/probes/c-apis
rm -rf "$D"; mkdir -p "$D"

cat > "$D/manifest.json" <<'JSON'
{
  "manifest_version": 2,
  "name": "API Probe",
  "version": "1.0",
  "permissions": [
    "alarms", "contextMenus", "privacy", "storage", "tabs",
    "unlimitedStorage", "webNavigation", "webRequest",
    "webRequestBlocking", "<all_urls>"
  ],
  "background": { "scripts": ["bg.js"], "persistent": true }
}
JSON

cat > "$D/bg.js" <<'JS'
var names = ["alarms","contextMenus","privacy","storage","tabs",
             "webNavigation","webRequest","runtime","extension","i18n"];
console.log("[PROBEC] start");
for (var i = 0; i < names.length; i++) {
  console.log("[PROBEC] " + names[i] + " = " + typeof chrome[names[i]]);
}
try {
  chrome.webRequest.onBeforeRequest.addListener(
    function (d) { return { cancel: true }; },
    { urls: ["*://*/*doubleclick*"] },
    ["blocking"]);
  console.log("[PROBEC] blocking listener OK");
} catch (e) {
  console.log("[PROBEC] blocking listener FAILED: " + e);
}
JS

adb push "$D" /sdcard/Download/
echo "liegt unter Download/c-apis"