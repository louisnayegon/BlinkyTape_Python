# -*- coding: utf-8 -*-
import tweepy
import twitter_monitor
from twitter_tags import twitter_tags
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
        if self.rgb == (0, 0, 0):
            return False

        self.count += 1
        if self.count >= self.ttl:
            self.rgb = (0, 0, 0)
            self.count = 0
            return False

        return True

    def set(self, rgb):
        self.rgb = rgb
        self.count = 0


class Strip:
    def __init__(self, blinky):
        self.num_of_lights = 60
        self.lights = deque([Light() for i in range(self.num_of_lights)])
        self.rgb = []
        self.blinky = blinky
        self.alive = 0

    def submit(self):
        self.process()
        self.blinky.send_list(self.rgb)

    def process(self):
        self.rgb = []
        self.alive = 0

        for light in self.lights:
            self.alive += light.tick()
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
        self.min_tick = 0.01
        self.max_tick = 0.1
        self.multiplier = (self.max_tick - self.min_tick) / self.strip1.num_of_lights

    def on_tweet(self, tweet):
        hashtags = []

        for obj in tweet['entities']['hashtags']:
            hashtags.append(obj['text'])

        print hashtags

        if hashtags:
            m = self.match(hashtags)
            self.strip1.set_rgb(0, m)

    def start(self, time=0.05):
        self.t = Timer(time, self.tick)
        self.t.start()

    def tick(self):
        self.strip1.cycle()
        self.strip1.submit()
        self.blinky.show()
        self.start(self.max_tick - (self.multiplier*self.strip1.alive))

    def match(self, strings):
        cleaned = [x.lower() for x in strings]

        for key, value in self.twitter_tags:
            if key.lower() in cleaned:
                return value['red'], value['green'], value['blue']


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


class DictionaryTermChecker(twitter_monitor.checker.TermChecker):
    """
    Checks for tracked terms in a file.
    """

    def __init__(self, dictionary):
        super(DictionaryTermChecker, self).__init__()
        self.dictionary = dictionary

    def update_tracking_terms(self):
        """
        Terms must be one-per-line.
        Blank lines will be skipped.
        """
        # build a set of terms
        new_terms = set()
        for key in self.dictionary:
            new_terms.add('#{}'.format(key))

        return set(new_terms)


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
    checker = DictionaryTermChecker(dictionary=twitter_tags)
    checker.update_tracking_terms()

    # Construct your own subclasses here instead

    vis = FourHorsesVisualisation(options.portname)
    listener = AwesomeListener(vis.on_tweet)

    vis.start()


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