import os
import tweepy
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

bearer_token = os.getenv("BEARER_TOKEN")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
twitter_id = os.getenv("TWITTER_ID")
callback = os.getenv("CALLBACK")

client = tweepy.Client(bearer_token=bearer_token)

response = client.get_users_following(twitter_id)
following_id_list = []
for user in response.data:
    following_id_list.append(user.id)

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

for user_id in following_id_list[0:50]:
    response = client.unfollow_user(user_id)
    print(response)
