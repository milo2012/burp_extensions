# burp_extensions
burp_extensions
  
- burp_random_token_generator.py

```
This is similar to https://github.com/portswigger/token-incrementor but 
doesn't work well for my test.
This is because Token Incrementor adds the Incremented text to every new 
token which might affect the testing.
Burp Extension in Python makes it easier to modify.
```
  
- chrome_sniffer
```
This burp extension is used for situations where the browser requires a 
certificate to connect to the website. The client only provides the 
certificate for the browser but not the root certificate required by Burp.
This script is half completed as it only intercepts GET requests 
``` 

