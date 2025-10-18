from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from config import Config
from models import SessionCreateRequest, ExecuteRequest
from session_manager import SessionManager
from proxy_client import ProxyClient
from auth import require_api_key, validate_session_api_key

app = Flask(__name__)
CORS(app)

session_manager = SessionManager()

Config.validate()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'base_url': Config.BASE_URL
    }), 200

@app.route('/api/v1/info', methods=['GET'])
@require_api_key
def get_api_info():
    return jsonify({
        'base_url': Config.BASE_URL,
        'api_version': 'v1',
        'endpoints': {
            'create_session': f"{Config.BASE_URL}/api/v1/sessions",
            'list_sessions': f"{Config.BASE_URL}/api/v1/sessions",
            'execute': f"{Config.BASE_URL}/api/v1/sessions/<session_id>/execute",
            'delete_session': f"{Config.BASE_URL}/api/v1/sessions/<session_id>"
        }
    }), 200

@app.route('/api/v1/sessions', methods=['POST'])
@require_api_key
def create_session():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'message': 'Expected JSON payload.'
            }), 400
        session_request = SessionCreateRequest(**data)
        session_info = session_manager.create_session(session_request)
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session_info.session_id,
                'api_key': session_info.api_key,
                'base_url': session_info.base_url,
                'target_url': str(session_info.target_url),
                'fields': [field.model_dump() for field in session_info.fields]
            }
        }), 201
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/sessions', methods=['GET'])
@require_api_key
def list_sessions():
    sessions = session_manager.list_sessions()
    return jsonify({
        'success': True,
        'sessions': sessions,
        'count': len(sessions)
    }), 200

@app.route('/api/v1/sessions/<session_id>', methods=['GET'])
@require_api_key
def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404
    
    return jsonify({
        'success': True,
        'session': {
            'session_id': session.session_id,
            'base_url': f"{Config.BASE_URL}/api/v1/sessions/{session.session_id}",
            'target_url': str(session.request_model.target.url),
            'created_at': session.created_at.isoformat() + 'Z',
            'fields': [field.model_dump() for field in session.request_model.input_mappings]
        }
    }), 200

@app.route('/api/v1/sessions/<session_id>/execute', methods=['POST'])
def execute_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404

    api_key = None
    if 'X-API-Key' in request.headers:
        api_key = request.headers.get('X-API-Key')
    elif 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
    
    if not api_key or not validate_session_api_key(api_key, session.api_key):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Invalid or missing session API key'
        }), 401

    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'message': 'Expected JSON payload.'
            }), 400
        execute_request = ExecuteRequest(**data)
        
        proxy_client = ProxyClient(session.request_model)
        
        response = proxy_client.execute(
            payload=execute_request.payload,
            extra_headers=execute_request.extra_headers,
            query_parameters=execute_request.query_parameters
        )
        
        return jsonify({
            'success': True,
            'response': {
                'status_code': response.status_code,
                'headers': response.headers,
                'url': response.url,
                'elapsed_ms': response.elapsed_ms,
                'body': response.body
            }
        }), 200
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/sessions/<session_id>', methods=['DELETE'])
@require_api_key
def delete_session(session_id: str):
    if session_manager.delete_session(session_id):
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
