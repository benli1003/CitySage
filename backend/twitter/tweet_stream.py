# Schedule the cron job to run the tweet scraper
import time
from twitter_trends import get_dc_trends
import json
import os

TWEETS_FILE = os.path.join(os.path.dirname(__file__), "cached_tweets.json")

# Eventually have this scheduled to run in intervals
# Call the get_dc_trends function to get the tending topics and then run search_tweets on each of them
def get_latest_trends():
    print("Fetching tweets...")
    tweets = get_dc_trends()
    tweets_by_trends = {
        trend: search_tweets(trend, max_results = 5)
        for trend in trends
    }
    return tweets_by_trends


# Write trends to the file
if __name__ == "__main__":
    tweets = get_latest_trends()
    with open("cached_tweets.json", "w") as f:
        json.dump(tweets, f, indent = 2)
