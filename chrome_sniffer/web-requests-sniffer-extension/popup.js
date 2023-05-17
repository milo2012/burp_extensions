document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("exportButton").addEventListener("click", function() {
    chrome.storage.local.get(null, function(items) {
      /*if (items.urls) {
        items.urls.forEach(function(url) {
          console.log(url.url);
        });
      }*/
      var data = JSON.stringify(items);
      var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.download = "local-storage-data.txt";
      a.href = url;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  });
});

