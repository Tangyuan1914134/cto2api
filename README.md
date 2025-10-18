# Web Reverse Proxy API

This project turns any web form into an API-driven interface by creating a reverse proxy service. Users can submit form inputs via REST API and retrieve real-time responses from the target website.

## Features
- Generate Base URL and API keys for each proxy session
- Secure API key authentication on both server and session level
- Map API payload to target web form fields
- Supports query parameters, form data, JSON payload, and header injection
- Returns detailed response including status code, headers, and response body
- Easily extensible configuration

## Getting Started

### Requirements
- Python 3.10+
- Pip or another Python package manager

### Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`.
3. Activate the environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`.
5. Copy `.env.example` to `.env` and update your API key and base URL.

### Run the Project
```
flask --app app run --host=0.0.0.0 --port=5000
```

The API will be available at `http://localhost:5000/`.

## Usage

### 1. Create a Session
`POST /api/v1/sessions`

Request Body:
```json
{
  "name": "Example Session",
  "description": "Proxy to example.com",
  "target": {
    "url": "https://httpbin.org/post",
    "method": "POST",
    "headers": {
      "User-Agent": "ProxyClient"
    }
  },
  "input_mappings": [
    {
      "input_key": "text",
      "target_field": "input",
      "transport": "form"
    }
  ]
}
```

Response:
```json
{
  "success": true,
  "session": {
    "session_id": "<session-id>",
    "api_key": "<generated-session-api-key>",
    "base_url": "http://localhost:5000/api/v1/sessions/<session-id>",
    "target_url": "https://httpbin.org/post",
    "fields": [
      {
        "input_key": "text",
        "target_field": "input",
        "transport": "form"
      }
    ]
  }
}
```

### 2. Execute Session
`POST /api/v1/sessions/<session_id>/execute`

Headers:
```
X-API-Key: <session-api-key>
```

Request Body:
```json
{
  "payload": {
    "text": "Hello World"
  }
}
```

Response:
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": { "Content-Type": "application/json" },
    "url": "https://httpbin.org/post",
    "elapsed_ms": 123.45,
    "body": "{...target response...}"
  }
}
```

### 3. List Sessions
`GET /api/v1/sessions`

### 4. Delete Session
`DELETE /api/v1/sessions/<session_id>`

## Security
- The API requires a master API key to create and manage sessions.
- Each session generates its own unique API key for executing inputs.

## License
MIT License
