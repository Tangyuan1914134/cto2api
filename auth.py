from functools import wraps
from flask import request, jsonify
from config import Config

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        
        if 'X-API-Key' in request.headers:
            api_key = request.headers.get('X-API-Key')
        elif 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        elif 'api_key' in request.args:
            api_key = request.args.get('api_key')
        
        if not api_key or api_key != Config.API_KEY:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key. Use X-API-Key header, Bearer token, or api_key query parameter.'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_session_api_key(session_api_key: str, stored_api_key: str) -> bool:
    return session_api_key == stored_api_key
