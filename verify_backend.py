import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def print_step(step):
    print(f"\n{'='*50}\n{step}\n{'='*50}")

def test_health():
    print_step("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return False

def test_auth():
    print_step("Testing Authentication")
    
    # Unique user for testing
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    password = "password123"
    
    print(f"Registering user: {username}")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    print(f"Register Status: {response.status_code}")
    print(f"Register Response: {response.json()}")
    
    # Login
    print(f"Logging in user: {username}")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    print(f"Login Status: {response.status_code}")
    data = response.json()
    print(f"Login Response: {data}")
    
    if response.status_code == 200:
        return data.get('access_token')
    return None

def test_classify(token):
    print_step("Testing Classification (IndoBERT)")
    
    text = "Saya sangat senang dengan pelayanan ini, luar biasa!"
    print(f"Input: {text}")
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
        
    response = requests.post(f"{BASE_URL}/api/classify", json={"text_input": text}, headers=headers)
    print(f"Classify Status: {response.status_code}")
    data = response.json()
    print(f"Classify Response: {data}")
    
    if response.status_code == 200:
        return data.get('id')
    return None

def test_history(token):
    print_step("Testing History")
    
    if not token:
        print("Skipping history test (no token)")
        return
        
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/history", headers=headers)
    print(f"History Status: {response.status_code}")
    print(f"History Response: {response.json()}")

def test_dashboard(token):
    print_step("Testing Dashboard APIs")
    headers = {'Authorization': f"Bearer {token}"}
    
    # Trend
    print("Fetching Trend Data...")
    res_trend = requests.get(f"{BASE_URL}/api/stats/trend", headers=headers)
    print(f"Trend Status: {res_trend.status_code}")
    
    # Word Cloud
    print("Fetching Word Cloud Data...")
    res_cloud = requests.get(f"{BASE_URL}/api/stats/wordcloud", headers=headers)
    print(f"Word Cloud Status: {res_cloud.status_code}")

def test_scraper():
    print_step("Testing Social Media Scraper")
    # Using a known safe URL (or mock if needed, but let's try a real one if possible, or skip if unstable)
    # For safety/speed, we might just check if the endpoint handles invalid URLs correctly first
    
    print("Testing Invalid URL...")
    res = requests.post(f"{BASE_URL}/api/scrape", json={"url": ""})
    print(f"Invalid URL Status: {res.status_code} (Expected 400)")
    
    # Optional: Test with a real URL if you want to verify functionality
    # url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    # res = requests.post(f"{BASE_URL}/api/scrape", json={"url": url})
    # print(f"Real URL Status: {res.status_code}")

def test_feedback(token, analysis_id):
    print_step("Testing Feedback Loop")
    headers = {'Authorization': f"Bearer {token}"}
    
    print(f"Submitting feedback for Analysis ID: {analysis_id}")
    res = requests.post(f"{BASE_URL}/api/feedback/{analysis_id}", 
                        json={"correction": "Negatif"}, 
                        headers=headers)
    print(f"Feedback Status: {res.status_code}")
    print(f"Feedback Response: {res.json()}")

if __name__ == "__main__":
    print("Checking if server is running...")
    if test_health():
        token = test_auth()
        if token:
            analysis_id = test_classify(token) # Update classify to return ID
            test_history(token)
            test_dashboard(token)
            test_scraper()
            if analysis_id:
                test_feedback(token, analysis_id)
    else:
        print("\n❌ Server is not running. Please run 'python app.py' first.")
