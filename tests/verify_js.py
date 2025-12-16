import requests
import time

def verify_auth_js():
    url = "http://127.0.0.1:5000/"
    print(f"Checking {url}...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Successfully accessed {url}")
            
            # Check for Auth object
            if "const Auth =" in response.text:
                print("✅ Found 'const Auth =' in response")
            else:
                print("❌ 'const Auth =' NOT found in response")
                
            # Check for specific JS content to verify embedding
            if "Auth.isLoggedIn()" in response.text:
                 print("✅ Found 'Auth.isLoggedIn()' usage in response")
            else:
                 print("❌ 'Auth.isLoggedIn()' usage NOT found in response")

            # Check for markdown artifacts (The bug we just fixed)
            if "```html" in response.text or "'''html" in response.text:
                print("❌ Found markdown artifacts (```html) in response! Fix failed.")
            else:
                print("✅ No markdown artifacts found in response.")

        else:
            print(f"❌ Failed to access {url}. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {url}. Is the server running?")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    verify_auth_js()
