import requests
from datetime import datetime, timedelta, timezone
import json
import random

# Moltbook API endpoint (v1 API - public, no authentication required)
API_URL = "https://www.moltbook.com/api/v1/posts"

# Time window: last 24 hours
TIME_WINDOW = 24  # hours

# Max posts to fetch
MAX_POSTS = 5
FETCH_BATCH = 30  # Fetch more posts to allow random selection

# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
}

def fetch_top_posts():
    try:
        # Calculate the timestamp for 24 hours ago (UTC)
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=TIME_WINDOW)

        # Parameters for the API request
        # Use 'new' sort to get recent posts, then randomly select
        params = {
            "sort": "new",
            "limit": FETCH_BATCH  # Fetch more to allow random selection
        }

        # Make the request (public API, no authentication needed)
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            posts = []
            
            # v1 API returns: {"success": true, "posts": [...], "count": N, ...}
            post_list = data.get("posts", [])
            
            for post in post_list:
                # Extract fields from v1 API response
                title = post.get("title", "Untitled")
                body = post.get("content", "")
                upvotes = post.get("upvotes", 0)
                comment_count = post.get("comment_count", 0)
                created_at = post.get("created_at", "")

                # Filter posts from last 24 hours
                if created_at:
                    try:
                        # Parse ISO 8601 timestamp (format: "2026-01-31T01:14:35.797843+00:00")
                        post_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        
                        # Check if within time window
                        if post_time < time_threshold:
                            continue
                    except Exception as e:
                        # If parsing fails, include the post anyway
                        pass

                # Format publication time to ISO 8601 with Z suffix
                published_at = created_at
                if published_at and not published_at.endswith("Z"):
                    # Convert +00:00 to Z
                    published_at = published_at.replace("+00:00", "Z")

                posts.append({
                    "title": title,
                    "body": body,
                    "published_at": published_at,
                    "upvotes": upvotes,
                    "comment_count": comment_count
                })

            # Randomly select MAX_POSTS from the filtered posts
            if len(posts) > MAX_POSTS:
                random.shuffle(posts)
                posts = posts[:MAX_POSTS]
            # If fewer than MAX_POSTS, keep all

            # Save to file
            with open("/root/clawd/skills/moltbook-fanboy/data/top_posts.json", "w") as f:
                json.dump(posts, f, indent=4)

            print(f"Fetched {len(posts)} top posts")
            return posts
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        print(f"Error fetching top posts: {str(e)}")
        return []

# Run the function if the script is called directly
if __name__ == "__main__":
    fetch_top_posts()
