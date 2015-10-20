## HorribleSubs Real-Time API (or nearly)

It is an attempt to make a wrapper of the only endpoint which HorribleSubs gives us.

It fetches it every 0.5 seconds, because I cannot wait more than 0.5 sec for animes.
After that, it adds what it is new in the cache.
I should also add a deep matcher, which could publish updates for each anime, for each new version, for each new provider online.
But I am too lazy for now.

It is pretty cool that I can do a get_latest from a WebSocket, and I can also subscribe to new_anime_released.
Have fun with that.

Powered by Holy Mother of Real Time API: Crossbar.io & WAMP.ws
