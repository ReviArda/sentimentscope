import sys
import os

# Add parent directory to path to import modules from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import get_mock_comments

def test_mock_generation():
    print("Testing Dynamic Mock Comment Generation...")
    
    # Request 30 comments (more than the old limit of 10)
    limit = 30
    comments = get_mock_comments('instagram', limit)
    
    print(f"Requested: {limit}")
    print(f"Generated: {len(comments)}")
    
    # Check uniqueness
    unique_comments = set(comments)
    print(f"Unique: {len(unique_comments)}")
    
    if len(comments) != len(unique_comments):
        print("❌ FAILED: Duplicates found!")
    else:
        print("✅ PASSED: All comments are unique.")
        
    print("\nSample Comments:")
    for i, c in enumerate(comments[:10]):
        print(f"{i+1}. {c}")

if __name__ == "__main__":
    test_mock_generation()
