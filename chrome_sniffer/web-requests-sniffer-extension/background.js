chrome.storage.local.set({
  'QUOTA_BYTES': 0
});

chrome.webRequest.onSendHeaders.addListener(
  function(details) {
    chrome.storage.local.get("domains", function(data) {
      if (data.domains) {
        var domains = data.domains.split("\n");
        for (var i = 0; i < domains.length; i++) {
          var url1 = new URL(details.url);
          if (url1.hostname.endsWith(domains[i])) {
            var url = details.url;
            console.log('URL: ' + url);
            var headers = details.requestHeaders.map(function(header) {
                if (!header.name.toLowerCase().startsWith("sec-")) {
                    return header.name + ': ' + header.value;
                } 
            }).filter(Boolean).join('\n');

            var data = {
              url: url,
              method: details.method,
              headers: btoa(headers),
              requestBody: null
            };    
            chrome.storage.local.get({urls: []}, function(result) {
              var urls = result.urls;
              urls.push(data);
              chrome.storage.local.set({urls: urls});
            });    
          }
        }
      }
    })
  },
  {
    urls: ["<all_urls>"]
  },
  ["requestHeaders","extraHeaders"]
);

chrome.devtools.network.onRequestFinished.addListener(request => {
  request.getContent((body) => {
    if (request.request && request.request.url) {
      if (request.request.url.includes('mail.yandex.com')) {

         //continue with custom code
         var bodyObj = JSON.parse(body);//etc.
      }
}
});
});
