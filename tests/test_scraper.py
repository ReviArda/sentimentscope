"""
Test script untuk social media scraper
"""
import sys
import os

# Add parent directory to path to import modules from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import (
    get_youtube_comments, 
    get_instagram_comments, 
    get_tiktok_comments, 
    get_twitter_comments,
    detect_platform
)

print("=" * 60)
print("TESTING SOCIAL MEDIA SCRAPER")
print("=" * 60)

# Test 1: Platform Detection
print("\n[TEST 1] Platform Detection")
print("-" * 60)
test_urls = {
    'youtube': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'instagram': 'https://www.instagram.com/p/ABC123/',
    'tiktok': 'https://www.tiktok.com/@user/video/1234567890',
    'twitter': 'https://twitter.com/user/status/1234567890'
}

for expected, url in test_urls.items():
    detected = detect_platform(url)
    status = "✅ PASS" if detected == expected else "❌ FAIL"
    print(f"{status} - {url} -> {detected}")

# Test 2: Instagram Scraper (will use mock data)
print("\n[TEST 2] Instagram Scraper")
print("-" * 60)
try:
    comments = get_instagram_comments('https://www.instagram.com/p/ABC123/', limit=5)
    print(f"✅ Got {len(comments)} comments")
    print(f"Sample: {comments[0][:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: TikTok Scraper (will use mock data)
print("\n[TEST 3] TikTok Scraper")
print("-" * 60)
try:
    comments = get_tiktok_comments('https://www.tiktok.com/@user/video/1234567890', limit=5)
    print(f"✅ Got {len(comments)} comments")
    print(f"Sample: {comments[0][:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Twitter Scraper (will use mock data)
print("\n[TEST 4] Twitter Scraper")
print("-" * 60)
try:
    comments = get_twitter_comments('https://twitter.com/user/status/1234567890', limit=5)
    print(f"✅ Got {len(comments)} comments")
    print(f"Sample: {comments[0][:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: YouTube Scraper (real scraping)
print("\n[TEST 5] YouTube Scraper (Real)")
print("-" * 60)
try:
    # Using a popular video that should have comments
    comments = get_youtube_comments('https://www.youtube.com/watch?v=dQw4w9WgXcQ', limit=3)
    print(f"✅ Got {len(comments)} real comments")
    if comments:
        print(f"Sample: {comments[0][:80]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
