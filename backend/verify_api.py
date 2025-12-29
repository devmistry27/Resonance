import requests
import json

def test_chat():
    url = "http://localhost:8002/v1/chat/completions"
    payload = {
        "session_id": "test_session",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "max_tokens": 50
        # No temperature passed, should default to 0.0 (greedy)
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Status: 200 OK")
            print("Response Body:")
            print(json.dumps(data, indent=2))
            
            content = data["message"]["content"]
            print(f"\nMessage Content: {content}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chat()
