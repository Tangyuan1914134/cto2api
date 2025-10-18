#!/bin/bash

API_BASE_URL="http://localhost:5000"
MASTER_API_KEY="default-api-key-please-change"

echo "=== Web Reverse Proxy API - cURL Examples ==="
echo ""

echo "1. Health Check"
curl -X GET "${API_BASE_URL}/health"
echo -e "\n\n"

echo "2. Get API Info"
curl -X GET "${API_BASE_URL}/api/v1/info" \
  -H "X-API-Key: ${MASTER_API_KEY}"
echo -e "\n\n"

echo "3. Create Session"
SESSION_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/v1/sessions" \
  -H "X-API-Key: ${MASTER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HTTPBin Test",
    "description": "Test session for httpbin.org",
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
  }')

echo "$SESSION_RESPONSE" | python3 -m json.tool
echo -e "\n"

SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session']['session_id'])" 2>/dev/null)
SESSION_API_KEY=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session']['api_key'])" 2>/dev/null)

if [ ! -z "$SESSION_ID" ]; then
  echo "Session ID: $SESSION_ID"
  echo "Session API Key: $SESSION_API_KEY"
  echo -e "\n"
  
  echo "4. Execute Session"
  curl -X POST "${API_BASE_URL}/api/v1/sessions/${SESSION_ID}/execute" \
    -H "X-API-Key: ${SESSION_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
      "payload": {
        "message": "Hello from cURL!",
        "user_id": "12345"
      }
    }' | python3 -m json.tool
  echo -e "\n\n"
  
  echo "5. Get Session Details"
  curl -X GET "${API_BASE_URL}/api/v1/sessions/${SESSION_ID}" \
    -H "X-API-Key: ${MASTER_API_KEY}" | python3 -m json.tool
  echo -e "\n\n"
  
  echo "6. List All Sessions"
  curl -X GET "${API_BASE_URL}/api/v1/sessions" \
    -H "X-API-Key: ${MASTER_API_KEY}" | python3 -m json.tool
  echo -e "\n\n"
  
  echo "7. Delete Session"
  curl -X DELETE "${API_BASE_URL}/api/v1/sessions/${SESSION_ID}" \
    -H "X-API-Key: ${MASTER_API_KEY}" | python3 -m json.tool
  echo -e "\n\n"
fi
