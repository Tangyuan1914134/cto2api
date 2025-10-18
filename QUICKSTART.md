# Quickstart Guide

Get started with Web Reverse Proxy API in 5 minutes!

## Step 1: Installation

```bash
# Clone the repository
git clone <repository-url>
cd web-reverse-proxy-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

## Step 2: Configure API Key

Edit `.env` file:
```
API_KEY=my-super-secret-key
BASE_URL=http://localhost:5000
PORT=5000
DEBUG=False
```

## Step 3: Start the Server

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

## Step 4: Test the API

### 4.1 Health Check
```bash
curl http://localhost:5000/health
```

### 4.2 Create a Session

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Session",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "message",
        "target_field": "message",
        "transport": "form"
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def",
    "api_key": "generated-session-key",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123-def",
    "target_url": "https://httpbin.org/post",
    "fields": [...]
  }
}
```

**Save the session_id and api_key!**

### 4.3 Execute the Session

Replace `<session-id>` and `<session-api-key>` with values from step 4.2:

```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "message": "Hello World!"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": {...},
    "url": "https://httpbin.org/post",
    "elapsed_ms": 234.56,
    "body": "..."
  }
}
```

## Step 5: Try More Examples

### Example: GET Request with Query Parameters

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Search API",
    "target": {
      "url": "https://httpbin.org/get",
      "method": "GET"
    },
    "input_mappings": [
      {
        "input_key": "query",
        "target_field": "q",
        "transport": "query"
      }
    ]
  }'
```

### Example: JSON Payload

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "JSON API",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST",
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "data",
        "target_field": "data",
        "transport": "json"
      }
    ]
  }'
```

### Example: Custom Headers

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Header API",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "auth_token",
        "target_field": "Authorization",
        "transport": "header"
      },
      {
        "input_key": "data",
        "target_field": "data",
        "transport": "form"
      }
    ]
  }'
```

## Next Steps

- Read the full [API Documentation](API_DOCUMENTATION.md)
- Check out [Examples](examples/)
- Import [Postman Collection](postman_collection.json)
- Deploy with [Docker](#docker-deployment)

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Common Issues

### Issue: "Unauthorized" Error
**Solution:** Make sure you're using the correct API key in the `X-API-Key` header.

### Issue: "Session not found"
**Solution:** Verify the session_id is correct and the session hasn't been deleted.

### Issue: Connection Refused
**Solution:** Ensure the Flask app is running on the correct port (default: 5000).

## Support

For more help:
- Check [README.md](README.md) for detailed information
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Read [README_CN.md](README_CN.md) for Chinese documentation
