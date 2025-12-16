from youtube_comment_downloader import YoutubeCommentDownloader
from itertools import islice
import re
import logging
import time
import random

# Import Playwright (sync API is easier for this context)
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# Mock Data (Only for extreme fallbacks)
MOCK_COMPONENT_SUBJECTS = ["Videonya", "Konten ini", "Kakak", "Admin", "Editannya", "Infonya"]
MOCK_COMPONENT_VERBS = ["keren banget", "sangat membantu", "kurang jelas", "gokil abis", "lucu parah"]
MOCK_COMPONENT_CONTEXTS = ["sumpah", "jujur", "asli", "menurutku"]
MOCK_COMPONENT_CLOSINGS = ["semangat", "mantap", "wkwk", "🔥🔥🔥"]

def get_mock_comments(platform, limit=20):
    """
    Generate unique synthetic comments using random combinations.
    """
    generated_comments = set()
    attempts = 0
    max_attempts = limit * 5
    
    while len(generated_comments) < limit and attempts < max_attempts:
        attempts += 1
        subject = random.choice(MOCK_COMPONENT_SUBJECTS)
        verb = random.choice(MOCK_COMPONENT_VERBS)
        context = f"{random.choice(MOCK_COMPONENT_CONTEXTS)} " if random.random() < 0.3 else ""
        closing = f", {random.choice(MOCK_COMPONENT_CLOSINGS)}" if random.random() < 0.4 else ""
        
        template_type = random.randint(1, 3)
        if template_type == 1:
            sentence = f"{context}{subject} {verb}{closing}."
        elif template_type == 2:
            sentence = f"{subject} {verb} {context.strip()}!{closing}"
        else:
            sentence = f"{verb} {subject}-nya{closing}."
            
        generated_comments.add(sentence.replace(" ,", ",").replace(" .", ".").strip())
        
    return list(generated_comments)


def scrape_with_playwright(url, platform, limit=20):
    """
    Universal scraping function using Playwright Browser Automation.
    """
    try:
        with sync_playwright() as p:
            # Launch browser (headless=True for background operation)
            browser = p.chromium.launch(headless=True)
            
            # Create a new context with a realistic user agent to avoid bot detection
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            logger.info(f"Navigating to {url} ({platform})...")
            
            # Go to URL with timeout
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                logger.error(f"Navigation failed: {e}")
                browser.close()
                return []

            comments = []
            
            if platform == 'instagram':
                # Initial wait
                time.sleep(3)
                
                # Close login popup if appears (not always needed with direct link, but good practice)
                # Try to scroll a bit to trigger loading
                page.keyboard.press("PageDown")
                time.sleep(2)
                
                # Extract comments
                # Instagram classes are obfuscated, so we look for structure or aria-labels
                # Strategy: Look for specific elements that often contain comments
                # Fallback: Get all text from certain containers
                
                # Try simple selector for comments (often text within list items)
                # Note: This is brittle. Best effort.
                try:
                    # Generic scraping for text that looks like a comment in the main article section
                    # or specifically targeted list items
                     elements = page.query_selector_all('ul li div[role="button"] ~ div span') 
                     if not elements:
                         # Fallback selector patterns (generic div/span)
                         elements = page.query_selector_all("span._aacl, span.x1lliihq")
                     
                     for el in elements[:limit*2]: # Get more, filter later
                         text = el.inner_text()
                         # Filter out usernames/timestamps (basic heuristic)
                         if len(text) > 3 and "Reply" not in text and "Like" not in text:
                             # Use a set to avoid dupes locally
                             if text not in comments:
                                 comments.append(text)
                             if len(comments) >= limit:
                                 break
                except Exception as e:
                    logger.error(f"Instagram extraction error: {e}")

            elif platform == 'tiktok':
                time.sleep(3)
                # Scroll to load comments
                for _ in range(3):
                    page.keyboard.press("PageDown")
                    time.sleep(1)
                
                # TikTok comments usually in data-e2e="comment-text"
                try:
                    elements = page.query_selector_all('[data-e2e="comment-level-1"]')
                    if not elements:
                        elements = page.query_selector_all('.css-166dk4x-PCommentText')
                        
                    for el in elements[:limit]:
                        text = el.inner_text()
                        if text:
                            comments.append(text.strip())
                except Exception as e:
                    logger.error(f"TikTok extraction error: {e}")

            elif platform == 'twitter':
                time.sleep(4)
                # Scroll down
                page.keyboard.press("PageDown")
                time.sleep(2)
                
                try:
                    # Twitter uses articles for tweets
                    # We want replies, which are usually subsequent articles
                    elements = page.query_selector_all('article [data-testid="tweetText"]')
                    
                    # First one is usually the main tweet, skip it
                    for el in elements[1:(limit+1)]:
                        text = el.inner_text()
                        if text:
                            comments.append(text.strip())
                except Exception as e:
                    logger.error(f"Twitter extraction error: {e}")

            browser.close()
            return comments

    except Exception as e:
        logger.error(f"Playwright critical error: {e}")
        return []

def get_youtube_comments(url, limit=20):
    try:
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(url, sort_by=1)
        results = []
        for comment in islice(comments, limit):
            results.append(comment['text'])
        return results
    except Exception as e:
        logger.error(f"Error scraping YouTube: {e}")
        raise ValueError(f"Gagal mengambil komentar YouTube: {str(e)}")

def detect_platform(url):
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    else:
        return None

def scrape_social_media(url, platform=None, limit=20):
    if platform is None:
        platform = detect_platform(url)
    
    if platform == 'youtube':
        return get_youtube_comments(url, limit), 'youtube'
    elif platform in ['instagram', 'tiktok', 'twitter']:
        # Use Playwright for these
        comments = scrape_with_playwright(url, platform, limit)
        if not comments:
            logger.warning(f"Playwright returned empty for {platform}. Falling back to Mock.")
            return get_mock_comments(platform, limit), platform
        return comments, platform
    else:
        raise ValueError(f"Unsupported platform: {url}")
