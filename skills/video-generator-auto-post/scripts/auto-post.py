#!/usr/bin/env python3
"""
Auto-post videos to social media platforms.
Usage: python auto-post.py video.mp4 --platforms twitter,tiktok,instagram
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VideoAutoPoster:
    def __init__(self):
        self.platforms = {
            'twitter': self.post_twitter,
            'tiktok': self.post_tiktok,
            'instagram': self.post_instagram,
            'linkedin': self.post_linkedin,
            'youtube': self.post_youtube_shorts,
        }
    
    def post_twitter(self, video_path, caption, hashtags):
        """Post to Twitter/X"""
        print(f"🐦 Posting to Twitter: {video_path}")
        print(f"   Caption: {caption}")
        print(f"   Hashtags: {' '.join(hashtags)}")
        # TODO: Implement Twitter API v2 upload
        # Requires: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN
        return True
    
    def post_tiktok(self, video_path, caption, hashtags):
        """Post to TikTok"""
        print(f"🎵 Posting to TikTok: {video_path}")
        print(f"   Caption: {caption}")
        print(f"   Hashtags: {' '.join(hashtags)}")
        # TODO: Implement TikTok Upload API
        # Requires: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
        return True
    
    def post_instagram(self, video_path, caption, hashtags):
        """Post to Instagram Reels"""
        print(f"📸 Posting to Instagram: {video_path}")
        print(f"   Caption: {caption}")
        print(f"   Hashtags: {' '.join(hashtags)}")
        # TODO: Implement Instagram Graph API
        # Requires: INSTAGRAM_TOKEN, INSTAGRAM_BUSINESS_ID
        return True
    
    def post_linkedin(self, video_path, caption, hashtags):
        """Post to LinkedIn"""
        print(f"💼 Posting to LinkedIn: {video_path}")
        print(f"   Caption: {caption}")
        print(f"   Hashtags: {' '.join(hashtags)}")
        # TODO: Implement LinkedIn API
        # Requires: LINKEDIN_ACCESS_TOKEN
        return True
    
    def post_youtube_shorts(self, video_path, caption, hashtags):
        """Post to YouTube Shorts"""
        print(f"▶️ Posting to YouTube Shorts: {video_path}")
        print(f"   Caption: {caption}")
        print(f"   Hashtags: {' '.join(hashtags)}")
        # TODO: Implement YouTube Data API
        # Requires: YOUTUBE_API_KEY
        return True
    
    def generate_caption(self, video_topic, style='engaging'):
        """Generate caption based on topic"""
        templates = {
            'engaging': [
                f"🔥 {video_topic} - What do you think?",
                f"✨ Just created this: {video_topic}",
                f"🤖 AI-generated: {video_topic} - Thoughts?",
            ],
            'professional': [
                f"Exploring {video_topic} with AI technology.",
                f"New experiment: {video_topic}",
                f"Innovation in action: {video_topic}",
            ],
            'funny': [
                f"POV: {video_topic} 😂",
                f"When AI tries {video_topic}... 💀",
                f"Nobody: ... AI: {video_topic}",
            ],
        }
        import random
        return random.choice(templates.get(style, templates['engaging']))
    
    def generate_hashtags(self, topic, count=10):
        """Generate relevant hashtags"""
        base_tags = ['#AI', '#AIVideo', '#GenerativeAI', '#TechTok', '#Innovation']
        topic_tags = [f'#{topic.replace(" ", "")}', f'#{topic}AI', f'#{topic}Video']
        
        all_tags = base_tags + topic_tags
        return all_tags[:count]
    
    def post(self, video_path, platforms='all', caption=None, hashtags=None, style='engaging'):
        """Main posting function"""
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"❌ Video file not found: {video_path}")
            return False
        
        # Generate caption and hashtags if not provided
        if not caption:
            caption = self.generate_caption(video_path.stem, style)
        
        if not hashtags:
            hashtags = self.generate_hashtags(video_path.stem)
        
        # Select platforms
        if platforms == 'all':
            selected = list(self.platforms.keys())
        else:
            selected = [p.strip() for p in platforms.split(',')]
        
        print(f"\n🦞 小龙虾 Auto-Poster")
        print(f"=" * 50)
        print(f"Video: {video_path.name}")
        print(f"Platforms: {', '.join(selected)}")
        print(f"=" * 50)
        
        # Post to each platform
        results = {}
        for platform in selected:
            if platform in self.platforms:
                try:
                    success = self.platforms[platform](str(video_path), caption, hashtags)
                    results[platform] = success
                except Exception as e:
                    print(f"❌ Error posting to {platform}: {e}")
                    results[platform] = False
            else:
                print(f"⚠️ Unknown platform: {platform}")
                results[platform] = False
        
        # Summary
        print(f"\n" + "=" * 50)
        print(f"Summary:")
        for platform, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {platform}")
        
        return all(results.values())

def main():
    parser = argparse.ArgumentParser(description='Auto-post AI videos to social media')
    parser.add_argument('video', help='Path to video file')
    parser.add_argument('--platforms', default='all', 
                       help='Comma-separated platforms (twitter,tiktok,instagram,linkedin,youtube)')
    parser.add_argument('--caption', help='Custom caption (auto-generated if not provided)')
    parser.add_argument('--hashtags', help='Custom hashtags (auto-generated if not provided)')
    parser.add_argument('--style', default='engaging', 
                       choices=['engaging', 'professional', 'funny'],
                       help='Caption style')
    
    args = parser.parse_args()
    
    poster = VideoAutoPoster()
    success = poster.post(
        args.video,
        platforms=args.platforms,
        caption=args.caption,
        hashtags=args.hashtags,
        style=args.style
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
