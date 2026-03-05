#!/usr/bin/env python3
"""
WordPress Post Publisher

A complete script to create and publish WordPress posts via REST API.
Supports Gutenberg blocks, categories, tags, featured images, and custom fields.

Usage:
    python wp_publish.py --title "Post Title" --content "Content" [options]
    python wp_publish.py --config config.json

Environment variables:
    WP_URL: WordPress site URL (e.g., https://example.com)
    WP_USERNAME: WordPress username
    WP_APPLICATION_PASSWORD: Application password (24 words)
"""

import argparse
import json
import os
import sys
import time
import requests
from typing import Dict, Any, Optional, List


class WordPressPublisher:
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize WordPress API client.
        
        Args:
            base_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            password: Application password (24 words) or regular password
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def test_connection(self) -> bool:
        """Test API connection and authentication."""
        try:
            response = self.session.get(f"{self.api_url}/users/me", timeout=10)
            if response.status_code == 200:
                print(f"✓ Connected as: {response.json().get('name')}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def upload_media(self, file_path: str, title: str = "", 
                     caption: str = "", alt_text: str = "") -> Optional[int]:
        """
        Upload media file to WordPress.
        
        Args:
            file_path: Path to image file
            title: Media title
            caption: Media caption
            alt_text: Alt text for accessibility
            
        Returns:
            Media ID or None if failed
        """
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {}
                if title:
                    data['title'] = title
                if caption:
                    data['caption'] = caption
                if alt_text:
                    data['alt_text'] = alt_text
                    
                response = self.session.post(
                    f"{self.api_url}/media",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    media_id = response.json()['id']
                    print(f"✓ Uploaded media: {file_path} (ID: {media_id})")
                    return media_id
                else:
                    print(f"✗ Upload failed: {response.status_code} {response.text}")
                    return None
                    
        except Exception as e:
            print(f"✗ Upload error: {e}")
            return None
    
    def get_or_create_category(self, category_name: str, 
                               parent_id: int = 0) -> Optional[int]:
        """
        Get existing category ID or create new category.
        
        Args:
            category_name: Category name
            parent_id: Parent category ID (0 for none)
            
        Returns:
            Category ID or None if failed
        """
        # Search for existing category
        response = self.session.get(
            f"{self.api_url}/categories",
            params={"search": category_name, "per_page": 5}
        )
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat['name'].lower() == category_name.lower():
                    print(f"✓ Found existing category: {category_name} (ID: {cat['id']})")
                    return cat['id']
        
        # Create new category
        data = {
            "name": category_name,
            "slug": category_name.lower().replace(' ', '-'),
            "parent": parent_id
        }
        
        response = self.session.post(f"{self.api_url}/categories", json=data)
        
        if response.status_code == 201:
            cat_id = response.json()['id']
            print(f"✓ Created category: {category_name} (ID: {cat_id})")
            return cat_id
        else:
            print(f"✗ Category creation failed: {response.status_code} {response.text}")
            return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """
        Get existing tag ID or create new tag.
        
        Args:
            tag_name: Tag name
            
        Returns:
            Tag ID or None if failed
        """
        # Search for existing tag
        response = self.session.get(
            f"{self.api_url}/tags",
            params={"search": tag_name, "per_page": 5}
        )
        
        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag['name'].lower() == tag_name.lower():
                    print(f"✓ Found existing tag: {tag_name} (ID: {tag['id']})")
                    return tag['id']
        
        # Create new tag
        data = {
            "name": tag_name,
            "slug": tag_name.lower().replace(' ', '-')
        }
        
        response = self.session.post(f"{self.api_url}/tags", json=data)
        
        if response.status_code == 201:
            tag_id = response.json()['id']
            print(f"✓ Created tag: {tag_name} (ID: {tag_id})")
            return tag_id
        else:
            print(f"✗ Tag creation failed: {response.status_code} {response.text}")
            return None
    
    def create_post(self, post_data: Dict[str, Any]) -> Optional[int]:
        """
        Create WordPress post.
        
        Args:
            post_data: Post data dictionary
            
        Returns:
            Post ID or None if failed
        """
        response = self.session.post(f"{self.api_url}/posts", json=post_data)
        
        if response.status_code == 201:
            post_id = response.json()['id']
            print(f"✓ Created post: {post_data.get('title', 'Untitled')} (ID: {post_id})")
            return post_id
        else:
            print(f"✗ Post creation failed: {response.status_code} {response.text}")
            return None
    
    def publish_post(self, post_id: int) -> bool:
        """
        Publish a draft post.
        
        Args:
            post_id: Post ID to publish
            
        Returns:
            True if successful
        """
        data = {"status": "publish"}
        response = self.session.post(f"{self.api_url}/posts/{post_id}", json=data)
        
        if response.status_code == 200:
            print(f"✓ Published post ID: {post_id}")
            return True
        else:
            print(f"✗ Publishing failed: {response.status_code} {response.text}")
            return False
    
    def create_post_from_config(self, config: Dict[str, Any]) -> Optional[int]:
        """
        Create post from configuration dictionary.
        
        Args:
            config: Configuration dictionary with post details
            
        Returns:
            Post ID or None if failed
        """
        # Process categories
        category_ids = []
        if 'categories' in config:
            for cat in config['categories']:
                if isinstance(cat, str):
                    cat_id = self.get_or_create_category(cat)
                    if cat_id:
                        category_ids.append(cat_id)
                elif isinstance(cat, dict):
                    cat_id = self.get_or_create_category(
                        cat.get('name'),
                        cat.get('parent', 0)
                    )
                    if cat_id:
                        category_ids.append(cat_id)
        
        # Process tags
        tag_ids = []
        if 'tags' in config:
            for tag in config['tags']:
                if isinstance(tag, str):
                    tag_id = self.get_or_create_tag(tag)
                    if tag_id:
                        tag_ids.append(tag_id)
        
        # Upload featured image
        featured_media = None
        if 'featured_image' in config:
            image_config = config['featured_image']
            if isinstance(image_config, str):
                featured_media = self.upload_media(image_config)
            elif isinstance(image_config, dict):
                featured_media = self.upload_media(
                    image_config.get('path', ''),
                    image_config.get('title', ''),
                    image_config.get('caption', ''),
                    image_config.get('alt_text', '')
                )
        
        # Prepare post data
        post_data = {
            "title": config.get('title', 'Untitled Post'),
            "content": config.get('content', ''),
            "excerpt": config.get('excerpt', ''),
            "status": config.get('status', 'draft'),
            "format": config.get('format', 'standard')
        }
        
        if category_ids:
            post_data["categories"] = category_ids
        if tag_ids:
            post_data["tags"] = tag_ids
        if featured_media:
            post_data["featured_media"] = featured_media
        
        if 'meta' in config:
            post_data["meta"] = config['meta']
        
        # Create post
        post_id = self.create_post(post_data)
        
        # Publish if requested
        if post_id and config.get('publish_immediately', False):
            time.sleep(2)  # Brief delay
            self.publish_post(post_id)
        
        return post_id


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='Publish WordPress posts via REST API')
    parser.add_argument('--title', help='Post title')
    parser.add_argument('--content', help='Post content (Gutenberg blocks)')
    parser.add_argument('--content-file', help='File containing post content')
    parser.add_argument('--excerpt', help='Post excerpt')
    parser.add_argument('--status', default='draft', 
                       choices=['draft', 'publish', 'pending', 'private'],
                       help='Post status')
    parser.add_argument('--categories', nargs='+', help='Category names')
    parser.add_argument('--tags', nargs='+', help='Tag names')
    parser.add_argument('--featured-image', help='Path to featured image')
    parser.add_argument('--config', help='JSON configuration file')
    parser.add_argument('--publish', action='store_true', 
                       help='Publish immediately (default: save as draft)')
    parser.add_argument('--test', action='store_true', 
                       help='Test connection only')
    
    args = parser.parse_args()
    
    # Load environment variables
    wp_url = os.environ.get('WP_URL')
    wp_username = os.environ.get('WP_USERNAME')
    wp_password = os.environ.get('WP_APPLICATION_PASSWORD')
    
    if not all([wp_url, wp_username, wp_password]):
        print("Error: Environment variables not set.")
        print("Please set: WP_URL, WP_USERNAME, WP_APPLICATION_PASSWORD")
        sys.exit(1)
    
    # Initialize publisher
    publisher = WordPressPublisher(wp_url, wp_username, wp_password)
    
    # Test connection
    if not publisher.test_connection():
        sys.exit(1)
    
    if args.test:
        print("✓ Connection test successful")
        sys.exit(0)
    
    # Load content from file if specified
    content = args.content
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    
    # Prepare configuration
    if args.config:
        config = load_config(args.config)
    else:
        config = {
            "title": args.title or "New Post",
            "content": content or "<!-- wp:paragraph --><p>Post content</p><!-- /wp:paragraph -->",
            "excerpt": args.excerpt or "",
            "status": "publish" if args.publish else args.status,
            "categories": args.categories or [],
            "tags": args.tags or [],
            "publish_immediately": args.publish
        }
        
        if args.featured_image:
            config["featured_image"] = args.featured_image
    
    # Create post
    post_id = publisher.create_post_from_config(config)
    
    if post_id:
        print(f"\n✓ Success! Post created with ID: {post_id}")
        print(f"   View: {wp_url}/wp-admin/post.php?post={post_id}&action=edit")
        print(f"   Preview: {wp_url}/?p={post_id}&preview=true")
        sys.exit(0)
    else:
        print("\n✗ Failed to create post")
        sys.exit(1)


if __name__ == "__main__":
    main()