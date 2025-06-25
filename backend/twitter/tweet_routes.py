# Handle routing and http requests from frontend
from flask import Blueprint, jsonify
from .twitter_trends import get_dc_trends
import json
import os

# Blueprint for all twitter related things
tweet_bp = Blueprint("tweet_bp", __name__)

# Cached tweets (going to schedule a cron job to query for new tweets in intervals)
TWEETS_FILE = os.path.join(os.path.dirname(__file__), "cached_tweets.json")

# Define a get request route to get the latest tweets. This will be purely reading
# from a file. Another function will handle writing to the file.

# grab latest 
@tweet_bp.route("/tweets/latest", methods = ["GET"])
def get_latest_tweets():
    if os.path.exists(TWEETS_FILE):
        with open(TWEETS_FILE, "r") as f:
            try:
                tweets = json.load(f)
                return jsonify(tweets)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format in cache."}), 500
    else:
        return jsonify({"error": "No tweets found."}), 404

@tweet_bp.route("/tweets/trends", methods = ["GET"])
def fetch_dc_trends():
    trends = get_dc_trends()
    return jsonify({"trends": trends})