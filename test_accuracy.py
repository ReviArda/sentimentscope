import requests
import json
import time

API_URL = "http://127.0.0.1:5000/api/classify"

test_cases = [
    # Positif
    {"text": "Pelayanan di restoran ini sangat memuaskan, makanannya lezat dan pelayannya ramah.", "expected": "Positif"},
    {"text": "Aplikasi ini sangat membantu pekerjaan saya, fiturnya lengkap dan mudah digunakan.", "expected": "Positif"},
    {"text": "Suka banget sama produk ini, kualitasnya oke punya!", "expected": "Positif"},
    
    # Negatif
    {"text": "Saya sangat kecewa dengan pelayanan toko ini, pengiriman lambat dan barang rusak.", "expected": "Negatif"},
    {"text": "Makanannya tidak enak, hambar dan harganya terlalu mahal.", "expected": "Negatif"},
    {"text": "Aplikasi ini sering crash dan sangat lambat, tolong diperbaiki segera.", "expected": "Negatif"},
    
    # Netral
    {"text": "Saya membeli buku ini di toko buku kemarin sore.", "expected": "Netral"},
    {"text": "Hari ini cuaca cukup cerah dengan sedikit awan.", "expected": "Netral"},
    {"text": "Pertemuan akan diadakan pada hari Senin pukul 10 pagi.", "expected": "Netral"}
]

def run_tests():
    print("STARTING TESTS...")
    passed = 0
    
    for case in test_cases:
        try:
            response = requests.post(API_URL, json={"text_input": case["text"]})
            if response.status_code == 200:
                data = response.json()
                actual = data["sentiment"]
                confidence = data['confidence']
                
                status = "PASS" if actual == case["expected"] else "FAIL"
                if status == "PASS":
                    passed += 1
                
                print(f"[{status}] Expected: {case['expected']}, Actual: {actual}, Conf: {confidence:.2%}")
                print(f"Text: {case['text']}")
                print("-" * 50)
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Connection Error: {e}")
            
    print(f"Total Passed: {passed}/{len(test_cases)}")

if __name__ == "__main__":
    print("Running Sentiment Accuracy Tests...\n")
    # Wait a bit to ensure server is ready if just started (though it's already running)
    time.sleep(1)
    run_tests()
