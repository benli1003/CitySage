import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Set the client
client = tweepy.Client(bearer_token = bearer_token)

# Tweet scraper function
def search_tweets(query, max_results):
    return client.search_recent_tweets(query = query, max_results = max_results)