from playwright.sync_api import sync_playwright
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_scrape(url, platform):
    print(f"\n[DEBUG] Starting debug scrape for: {url}")
    print("[DEBUG] Platform:", platform)
    print("[DEBUG] Browser will open in VISIBLE mode. Please watch the screen.")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        
        try:
            print("[DEBUG] Navigating...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(5) # Wait for initial load
            
            print("[DEBUG] Scroll & Wait...")
            page.keyboard.press("PageDown")
            time.sleep(2)
            page.keyboard.press("PageDown")
            time.sleep(2)
            
            # Check for common blockers
            content = page.content()
            if "Log in" in content or "Login" in content:
                print("[WARNING] 'Log in' detected in page text. Might be blocked.")
            
            comments = []
            
            # Try specific selectors based on platform
            if platform == 'instagram':
                # Try multiple Instagram selector patterns
                selectors = [
                    'span._aacl._aaco._aacu._aacx._aad7._aade', # Common comment text class
                    'ul li div[role="button"] ~ div span',      # Nested structure
                    'h3 + div > div > span',                    # Sometimes works
                    'div.x9f619 span'                           # Generic container
                ]
                
                print("[DEBUG] Trying Instagram selectors...")
                for sel in selectors:
                    elements = page.query_selector_all(sel)
                    print(f"  Selector '{sel}' found {len(elements)} elements")
                    for el in elements[:5]:
                        txt = el.inner_text()
                        if len(txt) > 3:
                            print(f"    - Found text: {txt[:50]}...")
                            comments.append(txt)
                            
            elif platform == 'tiktok':
                 # TikTok selectors
                 selectors = [
                     '[data-e2e="comment-text"]',
                     '.css-166dk4x-PCommentText',
                     'p[data-e2e="comment-level-1"]'
                 ]
                 
                 print("[DEBUG] Trying TikTok selectors...")
                 for sel in selectors:
                    elements = page.query_selector_all(sel)
                    print(f"  Selector '{sel}' found {len(elements)} elements")
                    for el in elements[:5]:
                        txt = el.inner_text()
                        print(f"    - Found text: {txt[:50]}...")
                        
            elif platform == 'twitter':
                 selectors = [
                     '[data-testid="tweetText"]'
                 ]
                 print("[DEBUG] Trying Twitter selectors...")
                 for sel in selectors:
                    elements = page.query_selector_all(sel)
                    print(f"  Selector '{sel}' found {len(elements)} elements")

            print(f"\n[SUMMARY] Total comments potentially found: {len(comments)}")
            
            # Keep browser open for a few seconds for user to see
            print("[DEBUG] Closing in 5 seconds...")
            time.sleep(5)
            
        except Exception as e:
            print(f"[ERROR] {e}")
            
        browser.close()

if __name__ == "__main__":
    # Example URL (Change this to test different links)
    # Using a trending / random public post likely to exist
    test_url = input("Masukkan URL Instagram/TikTok/Twitter untuk ditest: ")
    if "instagram" in test_url:
        debug_scrape(test_url, 'instagram')
    elif "tiktok" in test_url:
        debug_scrape(test_url, 'tiktok')
    elif "twitter" in test_url or "x.com" in test_url:
        debug_scrape(test_url, 'twitter')
    else:
        print("URL tidak dikenali.")
