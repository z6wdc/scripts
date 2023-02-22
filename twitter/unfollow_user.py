import os
import sys
import time

import tweepy
import threading
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

bearer_token = os.getenv("BEARER_TOKEN")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
twitter_id = os.getenv("TWITTER_ID")
callback = os.getenv("CALLBACK")


def unfollow_user(c, i, user):
    try:
        r = c.unfollow_user(user.id)
        if not r.data['following']:
            print(f"unfollow {i}th user: {user.name}\n")
    except tweepy.errors.TooManyRequests as e:
        print('TooManyRequests')


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

size = len(response.data)
threads = []

for index, following_user in enumerate(response.data):
    t = threading.Thread(target=unfollow_user, args=(client, index + 1, following_user))
    t.start()
    threads.append(t)
    if (index + 1) == size:
        break
    if (index + 1) % 50 == 0:
        time.sleep(60 * 15 + 30)  # sleep 15.5 minutes after 50 calls

for thread in threads:
    thread.join()

print("finish")
sys.exit()
