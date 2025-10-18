from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator

class InputMapping(BaseModel):
    input_key: str = Field(..., description="Key expected from API input")
    target_field: str = Field(..., description="Field name sent to target web form")
    transport: str = Field('form', description="Transport mechanism: form, query, header, json")

    @field_validator('transport')
    @classmethod
    def validate_transport(cls, v):
        if v not in {'form', 'query', 'header', 'json'}:
            raise ValueError('transport must be one of form, query, header, json')
        return v

class TargetConfig(BaseModel):
    url: HttpUrl
    method: str = Field('POST', description="HTTP method to call on target URL")
    headers: Dict[str, str] = Field(default_factory=dict)
    query_parameters: Dict[str, str] = Field(default_factory=dict)
    use_json: bool = Field(False, description="Send payload as JSON instead of form data")

    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        v_upper = v.upper()
        allowed = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}
        if v_upper not in allowed:
            raise ValueError(f'HTTP method {v} is not allowed. Use {allowed}')
        return v_upper

class SessionCreateRequest(BaseModel):
    name: str = Field(..., description="Human readable session name")
    description: Optional[str] = Field(None, description="Optional description")
    target: TargetConfig
    input_mappings: List[InputMapping]

class SessionInfo(BaseModel):
    session_id: str
    api_key: str
    base_url: str
    target_url: str
    fields: List[InputMapping]

class ExecuteRequest(BaseModel):
    payload: Dict[str, Any]
    extra_headers: Optional[Dict[str, str]] = None
    query_parameters: Optional[Dict[str, str]] = None

class ProxyResponse(BaseModel):
    status_code: int
    headers: Dict[str, Any]
    url: str
    elapsed_ms: float
    body: str
