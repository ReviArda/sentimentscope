from youtube_comment_downloader import YoutubeCommentDownloader
from itertools import islice

def get_youtube_comments(url, limit=20):
    """
    Fetches comments from a YouTube video URL.
    
    Args:
        url (str): The YouTube video URL.
        limit (int): Maximum number of comments to fetch.
        
    Returns:
        list: A list of comment texts.
    """
    try:
        downloader = YoutubeCommentDownloader()
        # sort_by=0 (popular), sort_by=1 (newest)
        comments = downloader.get_comments_from_url(url, sort_by=1)
        
        results = []
        for comment in islice(comments, limit):
            results.append(comment['text'])
            
        return results
    except Exception as e:
        print(f"Error scraping YouTube: {e}")
        return []
