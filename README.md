### little to say about the project, easy and lazy way to scrap v.

3 options:\
-parsing the html, get the ressources etc ...\
-have access to the API 😎, by tweaking the url ?\
-using selenium, playwright, fancy.

Parsing the html could be impossible, given the fact that the items wanted are
sometimes injected slightly after the base html appears...

Selenium etc ... would help you on that by waiting a little bit of time (time for the javascript to act)
but very slow and we want 0 delay on that.

So access the API is the best way, it gives you a perfect json to work with, but you got to have the formula for the url, turns out to be very easy.

The only thing you have to do is buy IP address from provider and inject it into your requests, or for testing purpose, using your phone's data...

aiohttp seems to be cook for scraping so going to curl_cffi instead, sad ...
