# -*- coding: utf-8 -*-
import tweepy
import twitter_monitor
import json
import time


class PrintingListener(twitter_monitor.JsonStreamListener):

    def on_status(self, status):
        text = status['text']
        print u'hello:{}'.format(text)
        #print json.dumps(status, indent=3)

    def on_limit(self, track):
        print "Horrors, we lost %d tweets!" % track

# The file containing terms to track
terms_filename = "tracking_terms.txt"

# How often to check the file for new terms
poll_interval = 15

# Your twitter API credentials
api_key = '6g9JBMkTpukVlRFW7Es5gJci0'
api_secret = '3VOUor6ukVwahUW5mTe90adUytgg759qwLQsFxT3jZuSZrgFnH'
access_token = '19641244-PCD9NcxrCoLBL7Tg9S95cBNypH8nc8eJ4JZayN6Dc'
access_token_secret = '2NDTQanVpIRbwEAz2YvKOSSLYWTOnl70LarSkfkW6KPok'

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)

# Construct your own subclasses here instead
listener = PrintingListener()
checker = twitter_monitor.checker.FileTermChecker(filename=terms_filename)
checker.update_tracking_terms()

# Start and maintain the streaming connection...
stream = twitter_monitor.DynamicTwitterStream(auth, listener, checker)
while True:
    try:
        # Loop and keep reconnecting in case something goes wrong
        # Note: You may annoy Twitter if you reconnect too often under some conditions.
        stream.start_polling(poll_interval)
    except Exception as e:
        print e
        time.sleep(1)  # to avoid craziness with Twitter
    