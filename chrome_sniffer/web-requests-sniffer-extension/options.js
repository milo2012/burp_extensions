document.addEventListener("DOMContentLoaded", function() {
  chrome.storage.local.get("domains", function(data) {
    if (data.domains) {
      document.getElementById("domains").value = data.domains;
    }
  });

  document.querySelector("form").addEventListener("submit", function(event) {
    event.preventDefault();
    var domains = document.getElementById("domains").value;
    chrome.storage.local.set({ "domains": domains });
  });
});