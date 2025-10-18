from typing import Dict, Any
import time

import requests
from requests import RequestException

from models import ProxyResponse, SessionCreateRequest

class ProxyClient:
    def __init__(self, session_request: SessionCreateRequest):
        self.session_request = session_request

    def execute(self, payload: Dict[str, Any], extra_headers: Dict[str, str] = None, query_parameters: Dict[str, str] = None) -> ProxyResponse:
        target = self.session_request.target

        headers = dict(target.headers or {})
        if extra_headers:
            headers.update(extra_headers)

        query_params = dict(target.query_parameters or {})
        if query_parameters:
            query_params.update(query_parameters)

        form_data = {}
        json_data = {}
        header_overrides = {}

        for mapping in self.session_request.input_mappings:
            if mapping.input_key not in payload:
                continue

            value = payload[mapping.input_key]

            if mapping.transport == 'form':
                form_data[mapping.target_field] = value
            elif mapping.transport == 'query':
                query_params[mapping.target_field] = value
            elif mapping.transport == 'header':
                header_overrides[mapping.target_field] = str(value)
            elif mapping.transport == 'json':
                json_data[mapping.target_field] = value

        if header_overrides:
            headers.update(header_overrides)

        request_kwargs: Dict[str, Any] = {
            'method': target.method,
            'url': str(target.url),
            'headers': headers,
            'params': query_params or None,
            'timeout': 30,
        }

        if target.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            if target.use_json or json_data:
                request_kwargs['json'] = json_data if json_data else payload
            else:
                request_kwargs['data'] = form_data
        else:
            request_kwargs['params'] = {**(request_kwargs['params'] or {}), **form_data}

        if json_data and not target.use_json:
            request_kwargs['json'] = json_data

        start_time = time.perf_counter()
        try:
            response = requests.request(**request_kwargs)
        except RequestException as exc:
            raise RuntimeError(f"Failed to execute proxy request: {exc}") from exc
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        response_headers = {k: v for k, v in response.headers.items()}

        return ProxyResponse(
            status_code=response.status_code,
            headers=response_headers,
            url=str(response.url),
            elapsed_ms=elapsed_ms,
            body=response.text
        )
