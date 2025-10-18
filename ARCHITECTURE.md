# Architecture Documentation

## Overview

The Web Reverse Proxy API is built using Flask framework and provides a clean RESTful API to proxy web requests with real-time input/output mapping.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
│              (Mobile App, Web App, Desktop App, etc.)           │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP/REST API
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     Web Reverse Proxy API                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Flask Application                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │ │
│  │  │   Auth       │  │   Session    │  │   Proxy        │  │ │
│  │  │   Manager    │  │   Manager    │  │   Client       │  │ │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP Request
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     Target Web Service                           │
│                  (Any HTTP/HTTPS endpoint)                       │
└──────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Application Layer (app.py)
- Main Flask application
- Route definitions
- Request/Response handling
- Error handling
- Middleware integration

### 2. Authentication Layer (auth.py)
- API key validation
- Two-tier authentication:
  - Master API key for session management
  - Session API key for execution
- Multiple authentication methods support

### 3. Session Management (session_manager.py)
- Session lifecycle management
- In-memory session storage
- Session CRUD operations
- Session metadata tracking

### 4. Proxy Client (proxy_client.py)
- HTTP request execution
- Field mapping transformation
- Support for multiple transport types
- Error handling and retries

### 5. Data Models (models.py)
- Pydantic models for data validation
- Request/Response schemas
- Type safety
- Auto-documentation support

### 6. Configuration (config.py)
- Environment-based configuration
- Centralized settings
- Validation rules

### 7. Utilities (utils.py)
- Helper functions
- API key generation
- Common utilities

## Data Flow

### Session Creation Flow

```
1. Client → POST /api/v1/sessions (with master API key)
2. AuthManager validates master API key
3. SessionManager creates new session
4. Generate unique session_id and api_key
5. Store session configuration
6. Return session credentials to client
```

### Request Execution Flow

```
1. Client → POST /api/v1/sessions/{id}/execute (with session API key)
2. AuthManager validates session API key
3. SessionManager retrieves session configuration
4. ProxyClient transforms request payload
   a. Apply input mappings
   b. Transform data based on transport type
   c. Build target request
5. Send request to target web service
6. Receive and process response
7. Return response to client
```

## Session Data Structure

```python
Session {
    session_id: str,
    api_key: str,
    request_model: {
        name: str,
        description: str,
        target: {
            url: HttpUrl,
            method: str,
            headers: dict,
            query_parameters: dict,
            use_json: bool
        },
        input_mappings: [
            {
                input_key: str,
                target_field: str,
                transport: str
            }
        ]
    },
    created_at: datetime,
    updated_at: datetime
}
```

## Transport Types

### 1. Form Transport (`transport: "form"`)
Sends data as `application/x-www-form-urlencoded`
```
Content-Type: application/x-www-form-urlencoded
field1=value1&field2=value2
```

### 2. Query Transport (`transport: "query"`)
Adds parameters to URL query string
```
https://example.com/api?param1=value1&param2=value2
```

### 3. Header Transport (`transport: "header"`)
Sends data as HTTP headers
```
Custom-Header: value1
X-User-ID: value2
```

### 4. JSON Transport (`transport: "json"`)
Sends data as JSON payload
```
Content-Type: application/json
{"field1": "value1", "field2": "value2"}
```

## Security Model

### Two-Tier Authentication

1. **Master API Key**
   - Server-level authentication
   - Used for session management
   - Set in environment configuration
   - Should be kept secret and rotated periodically

2. **Session API Key**
   - Session-level authentication
   - Unique per session
   - Auto-generated on session creation
   - Used only for executing requests

### Security Best Practices

1. Always use HTTPS in production
2. Rotate master API key regularly
3. Store API keys in environment variables
4. Never commit `.env` file to version control
5. Implement rate limiting (future feature)
6. Add IP whitelisting (future feature)

## Storage Strategy

### Current Implementation (In-Memory)
- Sessions stored in Python dictionary
- Fast access
- Lost on server restart
- Suitable for development and testing

### Future Enhancements
- Redis backend for session persistence
- Database storage for historical records
- Session TTL and expiration
- Session statistics and analytics

## Scalability Considerations

### Horizontal Scaling
- Stateless design (with external session storage)
- Load balancer compatible
- Multiple instances support (requires shared session store)

### Vertical Scaling
- Connection pooling
- Async request handling (future)
- Caching mechanisms
- Rate limiting

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message",
  "details": {}
}
```

### Error Categories
1. **400 Bad Request** - Invalid input data
2. **401 Unauthorized** - Authentication failure
3. **404 Not Found** - Session not found
4. **500 Internal Server Error** - Server-side errors

## Extension Points

### 1. Custom Authentication
Add custom authentication providers in `auth.py`

### 2. Custom Storage Backend
Implement custom session storage in `session_manager.py`

### 3. Request Transformers
Add custom request transformers in `proxy_client.py`

### 4. Middleware
Add Flask middleware for logging, monitoring, etc.

### 5. Webhooks
Implement webhook notifications for events

## Performance Metrics

Key metrics to monitor:
- Request latency (proxy overhead)
- Session count
- Request success rate
- API response time
- Target service response time

## Deployment Architecture

### Development
```
Local Machine → Flask Dev Server (port 5000)
```

### Production
```
Client → Load Balancer → Gunicorn/uWSGI → Flask App → Target Services
         └→ SSL/TLS     └→ Multiple workers
```

### Docker Deployment
```
Client → Docker Container (Flask + Gunicorn)
         └→ Volume mounts for configuration
         └→ Environment variables
```

## API Versioning

Current version: `v1`

API URL pattern: `/api/v1/...`

Future versions will maintain backward compatibility or introduce new endpoints.

## Logging and Monitoring

### Current Logging
- Flask default logging
- Console output

### Recommended Production Setup
- Structured logging (JSON format)
- Log aggregation (ELK, Splunk, CloudWatch)
- Application Performance Monitoring (APM)
- Error tracking (Sentry, Rollbar)

## Dependencies

### Core Dependencies
- Flask 3.0.0 - Web framework
- requests 2.31.0 - HTTP client
- pydantic 2.5.0 - Data validation
- python-dotenv 1.0.0 - Environment management

### Development Dependencies
- flask-cors - CORS support
- gunicorn - Production WSGI server

## Future Roadmap

1. **Phase 1 - Current**
   - Basic proxy functionality
   - Session management
   - Multiple transport types

2. **Phase 2**
   - Persistent session storage
   - Rate limiting
   - API usage analytics

3. **Phase 3**
   - WebSocket support
   - Async request handling
   - Caching layer

4. **Phase 4**
   - Plugin system
   - Custom middleware support
   - Advanced authentication methods
