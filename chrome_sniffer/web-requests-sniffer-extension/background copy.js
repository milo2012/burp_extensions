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
            var headers = details.responseHeaders;
            var requestBody = null;
            if (details.requestBody && details.requestBody.raw) {
                 requestBody = String.fromCharCode.apply(null, new Uint8Array(details.requestBody.raw[0].bytes));
            }
            var headers = details.requestHeaders.map(function(header) {
                if (!header.name.toLowerCase().startsWith("sec-")) {
                    return header.name + ': ' + header.value;
                } 
            }).filter(Boolean).join('\n');

            if (requestBody && requestBody.raw && requestBody.raw.length > 0) {
              requestBody = btoa(requestBody);
            }

            var data = {
              url: url,
              headers: btoa(headers),
              requestBody: requestBody
            };    
            //console.log('URL: ' + url);
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

