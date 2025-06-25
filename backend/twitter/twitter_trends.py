import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Return trending topics
def get_dc_trends():
    WOEID_DC = 2514815
    trends_result = api.get_place_trends(WOEID_DC)

    if trends_result:
        return [trend["name"] for trend in trends_result[0]["trends"]]
    else:
        return []
