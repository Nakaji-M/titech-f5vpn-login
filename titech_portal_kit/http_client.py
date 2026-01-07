import requests
import urllib.parse
from .request_models import HTTPRequest

class HTTPClientImpl:
    def __init__(self, user_agent: str):
        self.session = requests.Session()
        self.user_agent = user_agent

    def send(self, request: HTTPRequest) -> str:
        req = self._build_requests_req(request)
        response = self.session.send(req)
        response.encoding = 'utf-8' 
        return response.text

    def status_code(self, request: HTTPRequest) -> int:
        req = self._build_requests_req(request)
        response = self.session.send(req)
        return response.status_code

    def _build_requests_req(self, request: HTTPRequest) -> requests.PreparedRequest:
        url = request.url
        method = request.method
        headers = request.generate_headers(self.user_agent)
        
        data = None
        if request.body:
            safe_chars = "*"
            
            pairs = []
            for k, v in request.body.items():
                encoded_val = urllib.parse.quote(v, safe=safe_chars)
                
                encoded_key = urllib.parse.quote(k, safe=safe_chars)
                
                encoded_val = encoded_val.replace('%20', '+')
                encoded_key = encoded_key.replace('%20', '+')
                
                pairs.append(f"{encoded_key}={encoded_val}")
            
            data = "&".join(pairs)

        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            data=data if method == "POST" else None
        )
        return self.session.prepare_request(req)
