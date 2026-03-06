"""
Example usage for Composio Composer X Skill.
"""

from composio_composer_xskill import post_tweet, get_tweet, delete_tweet


def main():
    # Example: Post a tweet
    # Replace with your actual Composio auth token
    auth_token = "your_composio_auth_token_here"
    
    # Post a simple tweet
    result = post_tweet(
        content="Hello from OpenClaw! 🐾",
        composio_auth_token=auth_token
    )
    
    if result.get("success"):
        print(f"✅ Tweet posted successfully!")
        print(f"   Tweet ID: {result.get('tweet_id')}")
        print(f"   URL: {result.get('tweet_url')}")
        
        # Example: Get the tweet
        tweet_id = result.get("tweet_id")
        if tweet_id:
            get_result = get_tweet(tweet_id, auth_token)
            print(f"\n📄 Get tweet result: {get_result}")
            
            # Example: Delete the tweet
            delete_result = delete_tweet(tweet_id, auth_token)
            print(f"\n🗑️ Delete result: {delete_result}")
    else:
        print(f"❌ Failed to post tweet: {result.get('error')}")


if __name__ == "__main__":
    main()
