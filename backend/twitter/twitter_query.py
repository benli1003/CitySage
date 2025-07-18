# Handle specific queries made by the user for twitter
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Sends a get request to twitter api for relevant tweets. Returns a list of tweets.
def search_tweets(query, max_results = 10):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,text"
    }
    
    # Make the get request
    response = requests.get(url, headers=headers, params=params)
    
    # If sucessful, return a list of tweets, otherwise return an empty list
    if response.status_code == 429:
        print("Rate limit hit. ")
        return []
    elif response.status_code != 200:
        print(f"Twitter API Error: {response.status_code} - {response.text}")
        return []
   
    return response.json().get("data", [])
    
    