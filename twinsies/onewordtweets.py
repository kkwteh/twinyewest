
import tweepy
import json

from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
import os

CONSUMER_KEY = os.environ['OWT_API_KEY']
CONSUMER_SECRET = os.environ['OWT_API_SECRET']
ACCESS_TOKEN = os.environ['OWT_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['OWT_ACCESS_TOKEN_SECRET']

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tweet = None
        self.last_update = datetime(1999,1,1).timestamp()

    def on_data(self, data):
        tweet_dict = json.loads(data)
        words = tweet_dict['text'].strip().split() if 'text' in tweet_dict else []
        if (len(words) == 2 and words[1].startswith('https') and 'media' in tweet_dict['entities']):
            self.tweet = json.loads(data)

        if (datetime.now().timestamp() - self.last_update) > 15 * 60 and self.tweet:
            twitter_api().retweet(self.tweet['id'])
            self.last_udpate = datetime.now().timestamp()
        return True

    def on_error(self, status):
        print(status)

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)


if __name__ == '__main__':
    l = StdOutListener()

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l)
    letters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    stream.filter(track=letters, languages=['en'])
