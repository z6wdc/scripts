import os
import sys
import time

import tweepy
import threading
from queue import Queue
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

bearer_token = os.getenv("BEARER_TOKEN")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
twitter_id = os.getenv("TWITTER_ID")
callback = os.getenv("CALLBACK")

STATUS_429 = 'TooManyRequests'


def unfollow_user(c, i, user):
    try:
        r = c.unfollow_user(user.id)
        if not r.data['following']:
            q.put(f"unfollow {i}th user: {user.name}\n")
    except tweepy.errors.TooManyRequests:
        q.put(STATUS_429)


client = tweepy.Client(bearer_token=bearer_token)

response = client.get_users_following(twitter_id)
if len(response.data) == 0:
    sys.exit("Did not get a following list")

oauth1_user_handler = tweepy.OAuth1UserHandler(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    callback=callback
)

print(oauth1_user_handler.get_authorization_url(signin_with_twitter=True))
url = input("oauth_verifier:")

access_token, access_token_secret = oauth1_user_handler.get_access_token(url)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

q = Queue()
threads = []
results = []
size = len(response.data)

flag = False

for index, following_user in enumerate(response.data, start=1):
    t = threading.Thread(target=unfollow_user, args=(client, index, following_user))
    t.start()
    threads.append(t)

    if index % 50 == 0 or index == size:
        for thread in threads:
            if thread.is_alive():
                thread.join()

        for item in q.queue:
            if item == STATUS_429:
                flag = True
            else:
                results.append(item)

        threads.clear()
        results.sort()
        for result in results:
            print(result)

        if flag:
            print(STATUS_429)
            break

        if index == size:
            break

        with q.mutex:
            q.queue.clear()
        print("wait 15.5 minutes after 50 calls")
        time.sleep(60 * 15 + 30)

print("finish")
sys.exit()
