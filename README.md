fancy-elb-noc
=============
Called NOC but is really shorthand for 'all hands on deck if this wiggles too much'.
Please please forgive my lack of javascript respect. Last time I did anything with javascript, netscape was still *the* browser, as was java.


what do you get
-----------
* A graph of requests per second, errors per minute, and avg latency over an hour.
* left y-axis is used for count
* right y-axis is used for latency
* blue line request rate
* magenta line latency
* red column bars error rate (backend 5xx)


quick and dirty setup
-------------

```console
$ bundle install
$ echo "AWS_ACCESS_KEY_ID=the-id\nAWS_SECRET_ACCESS_KEY=the-secret > .env"
$ foreman start
```

basic troubleshooting: the javascript console is your friend, code is pretty liberal with `console.log()`


supported queryparams
----------
* `utc=1` use UTC time scale
* `elb=something` specify utc
* `flair=0` turn off rainbows and unicorns
* `latency_scale=3000` set number of miliseconds the latency scale on the right should be for your service.
* `unicorn_pct=0.4` set the chance a unicorn will show up randomly (no effect if `flair=0`)
* `error_scale_seconds=1` use per second scale on the error graph instead of minutes.


extra flair setup
-----------
* download some clouds and fires and modify noc.html to load them. I'd include mine but I don't know where I got them and don't want to get into any trouble :)
* download some (small) animated gifs and modify noc.html to load them. might I suggest unicorns or kitties or stars.

todo
-----------
* add caching (maybe in postgres)
* cleanup readme
* refactor metrics class
* better logging
* ui authentication
* gemify dirs
