# -*- coding: utf-8 -*-
import tweepy
import twitter_monitor
import optparse
from BlinkyTape import BlinkyTape
from collections import deque
import time
import json
from threading import Timer


class Light:
    def __init__(self, ttl=10000):
        self.rgb = (0, 0, 0)
        self.count = 0
        self.ttl = ttl

    def tick(self):
        self.count += 1
        if self.count >= self.ttl:
            self.rgb = (0, 0, 0)
            self.count = 0

    def set(self, rgb):
        self.rgb = rgb
        self.count = 0


class Strip:
    def __init__(self, blinky):
        self.num_of_lights = 60
        self.lights = deque([Light() for i in range(self.num_of_lights)])
        self.rgb = []
        self.blinky = blinky

    def submit(self):
        self.process()
        self.blinky.send_list(self.rgb)

    def process(self):
        self.rgb = []

        for light in self.lights:
            light.tick()
            self.rgb.append(light.rgb)

        return self.rgb

    def set_r_g_b(self, index, r, g, b):
        self.lights[index].rgb = (r, g, b)

    def set_rgb(self, index, rgb):
        self.lights[index].set(rgb)

    def cycle(self):
        light = self.lights.popleft()
        self.lights.append(light)

    def merge(self, strip):
        pass


class FourHorsesVisualisation:
    def __init__(self, port):
        self.t = None
        self.blinky = BlinkyTape(port)
        self.strip1 = Strip(self.blinky)

    def on_tweet(self, tweet):
        hashtags = []

        for obj in tweet['entities']['hashtags']:
            hashtags.append(obj['text'])

        print hashtags

        m = self.match(hashtags)
        self.strip1.set_rgb(0, m)

    def start(self):
        self.t = Timer(0.02, self.tick)
        self.t.start()

    def tick(self):
        self.strip1.cycle()
        self.strip1.submit()
        self.blinky.show()
        self.start()

    def match(self, strings):
        cleaned = [x.lower() for x in strings]

        if "iot" in cleaned:
            return 255, 0, 0
        if "privacy" in cleaned:
            return 0, 255, 0
        if "copyright" in cleaned:
            return 0, 0, 255
        if "opendata" in cleaned:
            return 128, 128, 128


class AwesomeListener(twitter_monitor.JsonStreamListener):
    def __init__(self, callback):
        super(AwesomeListener, self).__init__()
        self.callback = callback

    def on_status(self, tweet):
        self.callback(tweet)
        # print json.dumps(status, indent=3)

    def on_limit(self, track):
        print "Horrors, we lost %d tweets!" % track

    def streaming_exception(self):
        pass


def start():
    terms_filename = "tracking_terms.txt"  # How often to check the file for new terms
    poll_interval = 30

    # Your twitter API credentials
    api_key = '6g9JBMkTpukVlRFW7Es5gJci0'
    api_secret = '3VOUor6ukVwahUW5mTe90adUytgg759qwLQsFxT3jZuSZrgFnH'
    access_token = '19641244-PCD9NcxrCoLBL7Tg9S95cBNypH8nc8eJ4JZayN6Dc'
    access_token_secret = '2NDTQanVpIRbwEAz2YvKOSSLYWTOnl70LarSkfkW6KPok'

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Construct your own subclasses here instead

    vis = FourHorsesVisualisation(options.portname)
    listener = AwesomeListener(vis.on_tweet)

    vis.start()

    checker = twitter_monitor.checker.FileTermChecker(filename=terms_filename)
    checker.update_tracking_terms()

    # Start and maintain the streaming connection...
    stream = twitter_monitor.DynamicTwitterStream(auth, listener, checker)

    loop = True

    while loop:
        try:
            # Loop and keep reconnecting in case something goes wrong
            # Note: You may annoy Twitter if you reconnect too often under some conditions.
            stream.start_polling(poll_interval)
        except KeyboardInterrupt:
            loop = False
            stream.stop_polling()
        except Exception as e:
            print e
            time.sleep(1)  # to avoid craziness with Twitter

# ----------------------------------------
parser = optparse.OptionParser()
parser.add_option("-p", "--port", dest="portname", help="serial port (ex: /dev/ttyUSB0)", default=None)
(options, args) = parser.parse_args()

# test()
start()