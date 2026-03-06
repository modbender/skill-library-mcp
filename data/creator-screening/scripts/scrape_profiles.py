#!/usr/bin/env python3
"""
Scrape Instagram creator profiles via Memories.ai Video Metadata API.
Falls back to Apify if APIFY_API_KEY is set and Memories.ai fails.

Usage: python3 scrape_profiles.py --usernames "user1,user2" --platform instagram
       python3 scrape_profiles.py --urls "https://instagram.com/reel/ABC,https://instagram.com/reel/DEF"
Output: JSON with profile data + video metrics for each creator.
"""
import argparse, json, urllib.request, sys, os, time

MAVI_KEY = os.environ.get('MEMORIES_API_KEY', '')
MAVI_BASE = 'https://mavi-backend.memories.ai/serve/api/v2'
APIFY_KEY = os.environ.get('APIFY_API_KEY', '')

def mavi_metadata(video_url, channel='rapid'):
    """Get video metadata + owner profile via Memories.ai."""
    url = f'{MAVI_BASE}/instagram/video/metadata'
    body = {'video_url': video_url, 'channel': channel}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', MAVI_KEY)
    req.add_header('Content-Type', 'application/json')
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())
    if result.get('code') == '0000':
        return result.get('data', {}).get('data', {}).get('xdt_shortcode_media', {})
    return None

def scrape_via_memories(video_urls):
    """Build creator profiles from Memories.ai video metadata."""
    creators = {}
    
    for video_url in video_urls:
        video_url = video_url.strip().replace('/p/', '/reel/').replace('/reels/', '/reel/')
        print(f"  Fetching metadata: {video_url}", file=sys.stderr, flush=True)
        
        try:
            meta = mavi_metadata(video_url)
            if not meta:
                print(f"    No metadata returned", file=sys.stderr, flush=True)
                continue
            
            owner = meta.get('owner', {})
            username = owner.get('username', '?')
            
            # Initialize creator if new
            if username not in creators:
                creators[username] = {
                    'fullName': owner.get('full_name'),
                    'followers': owner.get('edge_followed_by', {}).get('count', 0),
                    'verified': owner.get('is_verified', False),
                    'profilePic': owner.get('profile_pic_url'),
                    'videos': [],
                }
            
            # Add video data
            caption_edges = meta.get('edge_media_to_caption', {}).get('edges', [])
            caption = caption_edges[0]['node']['text'] if caption_edges else ''
            comment_count = meta.get('edge_media_to_parent_comment', {}).get('count', 0)
            
            creators[username]['videos'].append({
                'url': video_url,
                'shortcode': meta.get('shortcode'),
                'views': meta.get('video_view_count', 0),
                'playCount': meta.get('video_play_count', 0),
                'duration': meta.get('video_duration', 0),
                'comments': comment_count,
                'caption': caption[:200],
                'hasAudio': meta.get('has_audio', True),
                'dimensions': meta.get('dimensions', {}),
                'audioInfo': meta.get('clips_music_attribution_info', {}),
            })
            
        except Exception as e:
            print(f"    Error: {e}", file=sys.stderr, flush=True)
        
        time.sleep(0.5)
    
    # Calculate aggregates
    for username, data in creators.items():
        videos = data['videos']
        if videos:
            data['avgViews'] = round(sum(v['views'] for v in videos) / len(videos))
            data['avgPlayCount'] = round(sum(v['playCount'] for v in videos) / len(videos))
            data['videoCount'] = len(videos)
    
    return creators

def scrape_via_apify(usernames):
    """Fallback: Scrape Instagram profiles via Apify."""
    if not APIFY_KEY:
        print("APIFY_API_KEY not set, cannot use fallback", file=sys.stderr)
        return {}
    
    url = f'https://api.apify.com/v2/acts/apify~instagram-profile-scraper/run-sync-get-dataset-items?token={APIFY_KEY}'
    body = {"usernames": usernames, "resultsLimit": 1}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    resp = urllib.request.urlopen(req, timeout=300)
    raw = json.loads(resp.read())
    
    results = {}
    for p in raw:
        username = p.get('username', '?')
        posts = p.get('latestPosts', [])
        videos = [v for v in posts if v.get('type') == 'Video']
        avg_views = sum(v.get('videoViewCount') or 0 for v in videos) / max(len(videos), 1)
        followers = p.get('followersCount') or 0
        
        results[username] = {
            'fullName': p.get('fullName'),
            'bio': p.get('biography'),
            'followers': followers,
            'posts': p.get('postsCount'),
            'verified': p.get('verified'),
            'category': p.get('businessCategoryName'),
            'avgViews': round(avg_views),
            'videoCount': len(videos),
            'videos': [{
                'url': v.get('url', '').replace('/p/', '/reel/'),
                'caption': (v.get('caption') or '')[:200],
                'views': v.get('videoViewCount', 0),
                'comments': v.get('commentsCount', 0),
            } for v in videos[:10]],
        }
    return results

def main():
    parser = argparse.ArgumentParser(description='Scrape creator profiles')
    parser.add_argument('--usernames', help='Comma-separated usernames (uses Apify fallback)')
    parser.add_argument('--urls', help='Comma-separated video URLs (uses Memories.ai)')
    parser.add_argument('--platform', default='instagram')
    parser.add_argument('--channel', default='rapid', help='Memories.ai channel: rapid, memories.ai, apify')
    parser.add_argument('--output', default='-')
    args = parser.parse_args()
    
    if args.urls:
        urls = [u.strip() for u in args.urls.split(',') if u.strip()]
        results = scrape_via_memories(urls)
    elif args.usernames:
        usernames = [u.strip().lstrip('@') for u in args.usernames.split(',') if u.strip()]
        # Try Apify for username-based lookup (Memories.ai needs video URLs)
        results = scrape_via_apify(usernames)
    else:
        print("Provide --urls or --usernames", file=sys.stderr)
        sys.exit(1)
    
    output = json.dumps(results, indent=2, default=str)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w') as f:
            f.write(output)

if __name__ == '__main__':
    main()
