from unittest import TestCase
from twinsies.twitter import (dig_for_twins, twitter_api, random_trend_query,
    update_status_text, Tweet, fetch_tweets, CONTACTED_SCREEN_NAMES)
from collections import namedtuple

class TwitterTests(TestCase):
    def test_api(self):
        api = twitter_api()

    def test_dig_for_twins(self):
        MockTweet = namedtuple('MockTweet', ['text', 'user', 'id'])
        MockUser = namedtuple('MockUser', ['screen_name'])
        tweets = [
            MockTweet('Hello world', MockUser('user1'), 1),
            MockTweet('Hello world', MockUser('user2'), 2)]
        res = dig_for_twins(tweets)
        self.assertEqual(len(res), 2)

    def test_dig_for_twins_repeat_user(self):
        MockTweet = namedtuple('MockTweet', ['text', 'user', 'id'])
        MockUser = namedtuple('MockUser', ['screen_name'])
        tweets = [
            MockTweet('Hello world', MockUser('user1'), 1),
            MockTweet('Hello world', MockUser('user1'), 2),
            MockTweet('Hello world', MockUser('user1'), 3)]
        res = dig_for_twins(tweets)
        self.assertIsNone(res)

    def test_dig_for_twins_contacted(self):
        CONTACTED_SCREEN_NAMES.add('user1')
        CONTACTED_SCREEN_NAMES.add('user2')
        CONTACTED_SCREEN_NAMES.add('user3')
        MockTweet = namedtuple('MockTweet', ['text', 'user', 'id'])
        MockUser = namedtuple('MockUser', ['screen_name'])
        tweets = [
            MockTweet('Hello world', MockUser('user1'), 1),
            MockTweet('Hello world', MockUser('user2'), 2),
            MockTweet('Hello world', MockUser('user3'), 3)]
        res = dig_for_twins(tweets)
        self.assertIsNone(res)

    def test_dig_for_twins_miss(self):
        MockTweet = namedtuple('MockTweet', ['text', 'user', 'id'])
        MockUser = namedtuple('MockUser', ['screen_name'])
        tweets = [
            MockTweet('Hello world', MockUser('user1'), 1),
            MockTweet('Different tweet', MockUser('user2'), 2)]
        res = dig_for_twins(tweets)
        self.assertIsNone(res)

    def test_update_status_text(self):
        tweets = [Tweet('awesome_sauce', 1, 'hello_world'), Tweet('internetdog', 2, 'hello_world')]
        res = update_status_text(tweets)
        self.assertEqual(res, ".@awesome_sauce @internetdog I'mma let you finish, but y'all just said the exact same thing - hello_world")

    def test_random_trend_query(self):
        random_trend_query()

    def test_fetch_tweets(self):
        res = fetch_tweets('twitter', fetch_size=2)
        self.assertEqual(len(tuple(res)), 2)
