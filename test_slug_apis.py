#!/usr/bin/env python3
"""
Quick test for slug-based video API endpoints
"""

import requests
import json
from datetime import datetime
import os
from pathlib import Path

# Load .env file
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()
BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/') + "/api"

def test_slug_based_apis():
    print("="*60)
    print("Testing Slug-Based Video API Endpoints")
    print("="*60)
    
    # Get a video with slug
    print("\n1. Getting videos to find one with slug...")
    response = requests.get(f"{BASE_URL}/videos", timeout=10)
    if response.status_code != 200:
        print(f"❌ Failed to get videos: {response.status_code}")
        return False
    
    videos = response.json()
    test_video = None
    for video in videos:
        if video.get('slug'):
            test_video = video
            break
    
    if not test_video:
        print("❌ No videos with slug found")
        return False
    
    video_slug = test_video['slug']
    video_id = test_video['id']
    print(f"✅ Found video with slug: {video_slug}")
    print(f"   Video ID: {video_id}")
    print(f"   Title: {test_video.get('title', 'Unknown')}")
    
    # Test 1: Toggle like with slug
    print(f"\n2. Testing toggle-like with slug '{video_slug}'...")
    initial_likes = test_video.get('likes', 0)
    like_payload = {"id": video_slug, "action": "like"}
    like_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
    if like_response.status_code == 200:
        liked_video = like_response.json()
        if liked_video.get('likes', 0) == initial_likes + 1:
            print(f"✅ Toggle-like with slug works! Likes: {initial_likes} → {liked_video['likes']}")
            # Unlike to restore
            requests.post(f"{BASE_URL}/videos/toggle-like", json={"id": video_slug, "action": "unlike"}, timeout=10)
        else:
            print(f"❌ Toggle-like with slug failed: likes not incremented correctly")
            return False
    else:
        print(f"❌ Toggle-like with slug failed: {like_response.status_code}")
        return False
    
    # Test 2: Increment views with slug
    print(f"\n3. Testing increment-views with slug '{video_slug}'...")
    initial_views = test_video.get('views', 0)
    views_payload = {"id": video_slug}
    views_response = requests.post(f"{BASE_URL}/videos/increment-views", json=views_payload, timeout=10)
    if views_response.status_code == 200:
        updated_video = views_response.json()
        if updated_video.get('views', 0) == initial_views + 1:
            print(f"✅ Increment-views with slug works! Views: {initial_views} → {updated_video['views']}")
        else:
            print(f"❌ Increment-views with slug failed: views not incremented correctly")
            return False
    else:
        print(f"❌ Increment-views with slug failed: {views_response.status_code}")
        return False
    
    # Test 3: Get comments with slug
    print(f"\n4. Testing get comments with slug '{video_slug}'...")
    comments_response = requests.get(f"{BASE_URL}/comments?videoId={video_slug}", timeout=10)
    if comments_response.status_code == 200:
        comments = comments_response.json()
        print(f"✅ Get comments with slug works! Retrieved {len(comments)} comments")
    else:
        print(f"❌ Get comments with slug failed: {comments_response.status_code}")
        return False
    
    # Test 4: Create comment with slug (for notification test)
    print(f"\n5. Testing create comment with slug '{video_slug}'...")
    comment_payload = {
        "videoId": video_slug,
        "userId": "test-user-slug",
        "userName": "Test User Slug",
        "userAvatar": "",
        "content": "Testing slug-based comment creation!",
        "parentId": None
    }
    comment_response = requests.post(f"{BASE_URL}/comments", json=comment_payload, timeout=10)
    if comment_response.status_code == 200:
        comment = comment_response.json()
        print(f"✅ Create comment with slug works! Comment ID: {comment['id']}")
        # Clean up
        requests.delete(f"{BASE_URL}/comments?id={comment['id']}", timeout=10)
    else:
        print(f"❌ Create comment with slug failed: {comment_response.status_code}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL SLUG-BASED API TESTS PASSED!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = test_slug_based_apis()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        exit(1)
