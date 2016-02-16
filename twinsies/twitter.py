import os
import tweepy
from collections import defaultdict
from toolz.dicttoolz import valfilter
import random

from collections import namedtuple
Tweet = namedtuple('Tweet', ['screen_name', 'tweet_id', 'text'])

CONSUMER_KEY = os.environ['TWITTER_API_KEY']
CONSUMER_SECRET = os.environ['TWITTER_API_SECRET']
ACCESS_KEY = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

SF_WOEID=2487956

CONTACTED_SCREEN_NAMES = set()

def update_status(tweets):
    text = update_status_text(tweets)
    api = twitter_api()
    api.update_status(text, in_reply_to_status_id=tweets[0].tweet_id)
    api.update_status(text, in_reply_to_status_id=tweets[1].tweet_id)

MAX_TWEET_LENGTH = 140

def update_status_text(tweets):
    CONTACTED_SCREEN_NAMES.add(tweets[0].screen_name)
    CONTACTED_SCREEN_NAMES.add(tweets[1].screen_name)

    assert len(tweets) == 2
    comment = "I'mma let you finish, but y'all just said the exact same thing"
    return '.@{screen_name1} @{screen_name2} {comment} - {text}'.format(
        screen_name1=tweets[0].screen_name,
        screen_name2=tweets[1].screen_name,
        comment=comment,
        text=tweets[0].text)[:MAX_TWEET_LENGTH]


def dig_for_twins(tweets):
    """Returns list of two random twinned tweets, if twins exist"""
    text_to_users = defaultdict(dict)
    for tweet in tweets:
        if 'RT' not in tweet.text and tweet.user.screen_name not in CONTACTED_SCREEN_NAMES:
            text_to_users[tweet.text][tweet.user.screen_name] = (tweet.id, tweet.text)

    twins = valfilter(lambda v: len(v) == 2, text_to_users)

    if len(twins) == 0:
        tweets = None
    else:
        text = random.choice(list(twins.keys()))
        random_sample = random.sample(list(twins[text].items()), 2)
        tweets = [Tweet(*flatten(data)) for data in random_sample]

    return tweets


def flatten(data):
    return (data[0], data[1][0], data[1][1])


def fetch_tweets(query, fetch_size=10000):
    assert fetch_size > 0
    api = twitter_api()
    return (tweet for tweet in tweepy.Cursor(api.search,
                               q=query,
                               result_type="recent",
                               include_entities=True,
                               lang="en").items(fetch_size))


def random_trend_query():
    api = twitter_api()
    sf_trends = api.trends_place(SF_WOEID)
    trend_queries = [trend['query'] for trend in sf_trends[0]['trends']]
    return random.choice(trend_queries)


def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)
