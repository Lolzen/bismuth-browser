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
