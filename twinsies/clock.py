from apscheduler.schedulers.blocking import BlockingScheduler

from twinsies.twitter import (random_trend_query, fetch_tweets, dig_for_twins,
    update_status)

from memory_profiler import profile

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=16)
@profile
def twinsy_finder(fetch_size=10000):
    print("Running twinsy finder...")
    fetched_tweets = fetch_tweets('Kanye', fetch_size=fetch_size)
    tweets = dig_for_twins(fetched_tweets)
    del fetched_tweets
    if tweets:
        print("Twins found, updating status.")
        update_status(tweets)
    else:
        print("No twins found.")

if __name__ == '__main__':
    twinsy_finder()
    print("Starting scheduler")
    sched.start()
