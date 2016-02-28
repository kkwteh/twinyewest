
import tweepy
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from memory_profiler import profile
import os
import time
import chess
import urllib.request

from collections import OrderedDict

CONSUMER_KEY = os.environ['TWEET_CHESS_API_KEY']
CONSUMER_SECRET = os.environ['TWEET_CHESS_API_SECRET']
ACCESS_TOKEN = os.environ['TWEET_CHESS_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['TWEET_CHESS_ACCESS_TOKEN_SECRET']
JIN_PREFIX = 'http://www.jinchess.com/chessboard/?p='

resources = {}

HANDLE = '@tweetplaychess'

class TweetChessListener(StreamListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_data(self, data):
        mention = json.loads(data)
        print (mention['user']['screen_name'])
        process_mention(mention)
        return True

    def on_error(self, status):
        print(status)

def process_mention(mention):
    if mention['id'] > resources['last_board_update_id']:
        move = get_move(mention)
        if move:
            print("Moving %s" % move)
            resources['board'].push_san(move)
            status = '.@%s made a move. %s to play' % (mention['user']['screen_name'], color_to_play(resources['board']))
            tweet_board(resources['board'], status)


def get_move(mention):
    words = set(mention['text'].strip().split()) if 'text' in mention else set()
    if len(words) != 2 or HANDLE not in words:
        return None

    a, b = tuple(words)
    move = a if HANDLE in b else b

    try:
        resources['board'].parse_san(move)
        return move
    except ValueError:
        return None

@profile
def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

def jin_chess_url(board):
    return JIN_PREFIX + str(board).replace(' ','').replace('\n', '').replace('.','-')

def tweet_board(board, status):
    urllib.request.urlretrieve(jin_chess_url(board), filename='board.png')
    update = resources['api'].update_with_media(filename='board.png', status=status)
    resources['last_board_update_id'] = update.id

def color_to_play(board):
    return "White" if board.turn else "Black"

if __name__ == '__main__':
    l = TweetChessListener()

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    stream = Stream(auth, l)

    resources['board'] = chess.Board()
    resources['api'] = twitter_api()
    tweet_board(resources['board'], 'New Game')

    stream.filter(track=['tweetplaychess'])
