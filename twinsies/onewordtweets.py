
import tweepy
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from memory_profiler import profile
import os

CONSUMER_KEY = os.environ['OWT_API_KEY']
CONSUMER_SECRET = os.environ['OWT_API_SECRET']
ACCESS_TOKEN = os.environ['OWT_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['OWT_ACCESS_TOKEN_SECRET']

TWEET_PERIOD_SECONDS = 300

last_updated = {'value': datetime(1999,1,1).timestamp()}
class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tweet = None

    def on_data(self, data):
        if (datetime.now().timestamp() - last_updated['value']) > TWEET_PERIOD_SECONDS:
            tweet_dict = json.loads(data)
            words = tweet_dict['text'].strip().split() if 'text' in tweet_dict else []
            if (len(words) == 2 and words[1].startswith('https') and 'media' in tweet_dict['entities']
                and not tweet_dict['possibly_sensitive']):
                print('tweet found')
                self.tweet = json.loads(data)

            if self.tweet:
                print('retweeting')
                twitter_api().retweet(self.tweet['id'])
                self.tweet = None
                last_updated['value'] = datetime.now().timestamp()
        return True

    def on_error(self, status):
        print(status)

@profile
def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


if __name__ == '__main__':
    l = StdOutListener()

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l)
    letters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    stream.filter(track=letters, languages=['en'])
