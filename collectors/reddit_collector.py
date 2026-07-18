"""
Collector -- Reddit via PRAW (OAuth, free tier: 100 richieste/min per client,
uso non commerciale/personale/ricerca -- il progetto rientra).

Da eseguire sul Mac, non nel sandbox Cowork (rete bloccata verso reddit.com).

PREREQUISITO -- vanno creati tu, non posso farlo io:
  1. https://www.reddit.com/prefs/apps -> "create another app..." -> tipo: script
  2. redirect uri: http://localhost:8080
  3. Imposta come variabili d'ambiente (NON nel codice, NON in chat):
       export REDDIT_CLIENT_ID="..."
       export REDDIT_CLIENT_SECRET="..."
       export REDDIT_USER_AGENT="sentiment-project/0.1 by u/tuo_username"

Uso:
    python3 collectors/reddit_collector.py [subreddit] [limit]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import praw
from datetime import datetime, timezone
from common import write_record, get_data_dir


def get_reddit_client():
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT")

    missing = [
        name
        for name, val in [
            ("REDDIT_CLIENT_ID", client_id),
            ("REDDIT_CLIENT_SECRET", client_secret),
            ("REDDIT_USER_AGENT", user_agent),
        ]
        if not val
    ]
    if missing:
        print(f"Variabili d'ambiente mancanti: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)


def to_record(post, subreddit_name):
    return {
        "created_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
        "query_or_context": subreddit_name,
        "external_id": post.id,
        "author": str(post.author) if post.author else None,
        "text": f"{post.title}\n\n{post.selftext or ''}".strip(),
        "engagement": {
            "score": post.score,
            "num_comments": post.num_comments,
            "upvote_ratio": post.upvote_ratio,
        },
        "raw": {"permalink": post.permalink, "url": post.url},
    }


if __name__ == "__main__":
    sub_name = sys.argv[1] if len(sys.argv) > 1 else "stocks"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25

    reddit = get_reddit_client()
    reddit.read_only = True
    posts = list(reddit.subreddit(sub_name).hot(limit=limit))

    for post in posts:
        write_record("reddit", to_record(post, sub_name))

    print(f"Salvati {len(posts)} record da r/{sub_name} in {get_data_dir()}/reddit/")
    for post in posts[:10]:
        print(f"  [{post.score:>5}] {post.title[:80]}")
