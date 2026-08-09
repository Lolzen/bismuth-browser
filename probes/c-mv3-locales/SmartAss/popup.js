// popup.js — SmartAss (privat angepasste derStandard Comment Ranker)
// Reduziertes Popup: nur Icon/Titel + Ein/Aus-Toggle.

var SORT_KEY = 'dstSorterEnabled';
var toggle = document.getElementById('extensionEnabled');

function sendMessageToTab(msg) {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    if (tabs[0] && tabs[0].id) {
      chrome.tabs.sendMessage(tabs[0].id, msg).catch(function() {});
    }
  });
}

// Load saved state
chrome.storage.sync.get([SORT_KEY], function(data) {
  toggle.checked = data[SORT_KEY] !== false;
});

// Handle toggle
toggle.addEventListener('change', function() {
  var enabled = toggle.checked;
  chrome.storage.sync.set({ [SORT_KEY]: enabled });
  sendMessageToTab({ action: 'toggle', enabled: enabled });
});
