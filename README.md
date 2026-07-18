# sentiment-reddit-collector

Personal, non-commercial, read-only Reddit collector for a sentiment-analysis
research project. Uses PRAW (OAuth2, script-type app), `reddit.read_only = True`.
Fetches public "hot" post data (title, text, score, comments, timestamp) from a
small set of subreddits. Never posts, comments, votes, or writes anything to Reddit.

## Setup
    pip install -r requirements.txt
    export REDDIT_CLIENT_ID="..."
    export REDDIT_CLIENT_SECRET="..."
    export REDDIT_USER_AGENT="sentiment-project/0.1 by u/tuo_username"
    python3 collectors/reddit_collector.py wallstreetbets 25
