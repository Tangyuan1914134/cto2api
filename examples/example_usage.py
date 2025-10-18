import requests
import json

API_BASE_URL = "http://localhost:5000"
MASTER_API_KEY = "your-api-key-here"

def create_session():
    url = f"{API_BASE_URL}/api/v1/sessions"
    headers = {
        "X-API-Key": MASTER_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "name": "HTTPBin Test Session",
        "description": "Test session using httpbin.org",
        "target": {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {
                "User-Agent": "WebReverseProxyAPI/1.0"
            }
        },
        "input_mappings": [
            {
                "input_key": "message",
                "target_field": "message",
                "transport": "form"
            },
            {
                "input_key": "user_id",
                "target_field": "user_id",
                "transport": "form"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("Create Session Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def execute_session(session_id, session_api_key):
    url = f"{API_BASE_URL}/api/v1/sessions/{session_id}/execute"
    headers = {
        "X-API-Key": session_api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "payload": {
            "message": "Hello from Web Reverse Proxy API!",
            "user_id": "12345"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("\nExecute Session Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def list_sessions():
    url = f"{API_BASE_URL}/api/v1/sessions"
    headers = {
        "X-API-Key": MASTER_API_KEY
    }
    
    response = requests.get(url, headers=headers)
    print("\nList Sessions Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    print("=== Web Reverse Proxy API - Example Usage ===\n")
    
    session_response = create_session()
    
    if session_response.get('success'):
        session_id = session_response['session']['session_id']
        session_api_key = session_response['session']['api_key']
        
        execute_result = execute_session(session_id, session_api_key)
        
        list_sessions()
    else:
        print("Failed to create session!")
