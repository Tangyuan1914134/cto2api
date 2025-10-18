import uuid
from datetime import datetime
from typing import Dict, Optional

from models import SessionCreateRequest, SessionInfo
from config import Config
from utils import generate_api_key

class Session:
    def __init__(self, session_id: str, api_key: str, request_model: SessionCreateRequest):
        self.session_id = session_id
        self.api_key = api_key
        self.request_model = request_model
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, request_model: SessionCreateRequest) -> SessionInfo:
        session_id = str(uuid.uuid4())
        api_key = generate_api_key()
        session = Session(session_id=session_id, api_key=api_key, request_model=request_model)
        self.sessions[session_id] = session

        base_url = f"{Config.BASE_URL}/api/v1/sessions/{session_id}"

        return SessionInfo(
            session_id=session_id,
            api_key=api_key,
            base_url=base_url,
            target_url=str(request_model.target.url),
            fields=request_model.input_mappings
        )

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self):
        return [
            {
                'session_id': session.session_id,
                'base_url': f"{Config.BASE_URL}/api/v1/sessions/{session.session_id}",
                'target_url': str(session.request_model.target.url),
                'created_at': session.created_at.isoformat() + 'Z'
            }
            for session in self.sessions.values()
        ]
