# API Documentation

## Base URL
`http://localhost:5000` (configurable in `.env`)

## Authentication

### Master API Key
Used for session management operations (create, list, delete sessions).

**Methods:**
- Header: `X-API-Key: your-master-api-key`
- Authorization header: `Authorization: Bearer your-master-api-key`
- Query parameter: `?api_key=your-master-api-key`

### Session API Key
Used for executing requests through a specific session. Generated when creating a session.

**Methods:**
- Header: `X-API-Key: session-api-key`
- Authorization header: `Authorization: Bearer session-api-key`

## Endpoints

### Health Check
**GET** `/health`

No authentication required.

**Response:**
```json
{
  "status": "healthy",
  "base_url": "http://localhost:5000"
}
```

---

### Get API Information
**GET** `/api/v1/info`

**Authentication:** Master API Key

**Response:**
```json
{
  "base_url": "http://localhost:5000",
  "api_version": "v1",
  "endpoints": {
    "create_session": "http://localhost:5000/api/v1/sessions",
    "list_sessions": "http://localhost:5000/api/v1/sessions",
    "execute": "http://localhost:5000/api/v1/sessions/<session_id>/execute",
    "delete_session": "http://localhost:5000/api/v1/sessions/<session_id>"
  }
}
```

---

### Create Session
**POST** `/api/v1/sessions`

**Authentication:** Master API Key

**Request Body:**
```json
{
  "name": "Session Name",
  "description": "Optional description",
  "target": {
    "url": "https://example.com/form",
    "method": "POST",
    "headers": {
      "Custom-Header": "value"
    },
    "query_parameters": {
      "param1": "value1"
    },
    "use_json": false
  },
  "input_mappings": [
    {
      "input_key": "api_field_name",
      "target_field": "web_form_field_name",
      "transport": "form"
    }
  ]
}
```

**Fields:**

- `name` (string, required): Human-readable session name
- `description` (string, optional): Session description
- `target.url` (string, required): Target web URL to proxy to
- `target.method` (string, default: "POST"): HTTP method (GET, POST, PUT, DELETE, PATCH)
- `target.headers` (object, optional): Custom headers to send
- `target.query_parameters` (object, optional): Static query parameters
- `target.use_json` (boolean, default: false): Send as JSON payload instead of form data
- `input_mappings` (array, required): Field mapping configuration
  - `input_key` (string): Field name in API request
  - `target_field` (string): Field name in target web form
  - `transport` (string): Transport mechanism: "form", "query", "header", "json"

**Transport Types:**
- `form`: Send as form data (application/x-www-form-urlencoded)
- `query`: Add to URL query parameters
- `header`: Send as HTTP header
- `json`: Send in JSON body

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def-456",
    "api_key": "generated-session-api-key",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123-def-456",
    "target_url": "https://example.com/form",
    "fields": [...]
  }
}
```

---

### List Sessions
**GET** `/api/v1/sessions`

**Authentication:** Master API Key

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "abc-123",
      "base_url": "http://localhost:5000/api/v1/sessions/abc-123",
      "target_url": "https://example.com",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

---

### Get Session Details
**GET** `/api/v1/sessions/<session_id>`

**Authentication:** Master API Key

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123",
    "target_url": "https://example.com",
    "created_at": "2023-01-01T00:00:00Z",
    "fields": [...]
  }
}
```

---

### Execute Session
**POST** `/api/v1/sessions/<session_id>/execute`

**Authentication:** Session API Key (from create session response)

**Request Body:**
```json
{
  "payload": {
    "field1": "value1",
    "field2": "value2"
  },
  "extra_headers": {
    "Custom-Header": "value"
  },
  "query_parameters": {
    "param": "value"
  }
}
```

**Fields:**
- `payload` (object, required): Data to send (field names must match input_mappings)
- `extra_headers` (object, optional): Additional headers for this request
- `query_parameters` (object, optional): Additional query parameters for this request

**Response:**
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": {
      "content-type": "application/json"
    },
    "url": "https://example.com/form",
    "elapsed_ms": 234.56,
    "body": "Response from target website"
  }
}
```

---

### Delete Session
**DELETE** `/api/v1/sessions/<session_id>`

**Authentication:** Master API Key

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

## Example Workflows

### Example 1: Simple Form Proxy

**Step 1: Create Session**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contact Form",
    "target": {
      "url": "https://example.com/contact",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "name",
        "target_field": "full_name",
        "transport": "form"
      },
      {
        "input_key": "email",
        "target_field": "email_address",
        "transport": "form"
      }
    ]
  }'
```

**Step 2: Execute Request**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### Example 2: API with Headers and Query Params

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Proxy",
    "target": {
      "url": "https://api.example.com/data",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer static-token"
      },
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "data",
        "target_field": "payload",
        "transport": "json"
      },
      {
        "input_key": "user_id",
        "target_field": "user",
        "transport": "query"
      }
    ]
  }'
```

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "details": {}
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Validation error
- `401`: Unauthorized (invalid API key)
- `404`: Not found
- `500`: Internal server error
