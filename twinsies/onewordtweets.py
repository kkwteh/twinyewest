
import tweepy
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from memory_profiler import profile
import os
import time

from collections import OrderedDict

CONSUMER_KEY = os.environ['OWT_API_KEY']
CONSUMER_SECRET = os.environ['OWT_API_SECRET']
ACCESS_TOKEN = os.environ['OWT_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['OWT_ACCESS_TOKEN_SECRET']

TWEET_PERIOD_SECONDS = 300
LETTERS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

last_updated = {'value': datetime(1999,1,1).timestamp()}

#Maps word to (screen_name, tweet_id, link)
words_encountered = OrderedDict()
boring_words = {'Mood', 'Test'}
MAX_WORDS = 1000

class OneWordTweetListener(StreamListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_data(self, data):
        tweet_dict = json.loads(data)
        words = tweet_dict['text'].strip().split() if 'text' in tweet_dict else []
        if is_one_word_tweet(tweet_dict, words):
            normalized_word = normalize_word(words[0])
            print('tweet found: %s' % normalized_word)
            if normalized_word in words_encountered:
                print('twin found')
                words_encountered[normalized_word].append((tweet_dict['user']['screen_name'], tweet_dict['id'], words[1]))
            else:
                words_encountered[normalized_word] = [(tweet_dict['user']['screen_name'], tweet_dict['id'], words[1])]


            if len(words_encountered) > MAX_WORDS:
                old_key = list(words_encountered.keys())[0]
                del words_encountered[old_key]

            if (datetime.now().timestamp() - last_updated['value']) > TWEET_PERIOD_SECONDS:
                for key in list(words_encountered.keys()):
                    if len(words_encountered[key]) > 1 and key not in boring_words:
                        print('tweeting pair')
                        tweet_pair(words_encountered, key)
                        del words_encountered[key]
                        last_updated['value'] = datetime.now().timestamp()
                        break
        return True

    def on_error(self, status):
        print(status)

@profile
def tweet_pair(words_encountered, key):
    tweeters = set()
    names = [name for name, _, _ in words_encountered[key]]
    if len(names) == len(set(names)):
        api = twitter_api()
        for _, tweet_id, _ in words_encountered[key]:
            try:
                api.retweet(tweet_id)
            except tweepy.TweepError:
                pass
            time.sleep(1)

def is_one_word_tweet(tweet_dict, words):
    return (len(words) == 2 and
        words[1].startswith('https') and
        'media' in tweet_dict['entities'] and
        not tweet_dict['possibly_sensitive'])

def normalize_word(word):
    return ''.join([x for x in word if x in LETTERS]).title()

@profile
def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


if __name__ == '__main__':
    l = OneWordTweetListener()

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l)
    stream.filter(track=LETTERS, languages=['en'])
