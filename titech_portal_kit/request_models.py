from dataclasses import dataclass, field
from typing import Dict, Optional, List
from .utils import HTMLInput, HTMLSelect
BASE_ORIGIN_PROD = "https://portal.nap.gsic.titech.ac.jp"
BASE_HOST_PROD = "portal.nap.gsic.titech.ac.jp"
BASE_ORIGIN_MOCK = "https://portal-mock.titech.app"
BASE_HOST_MOCK = "portal-mock.titech.app"

class BaseURL:
    origin = BASE_ORIGIN_PROD
    host = BASE_HOST_PROD

    @classmethod
    def change_to_mock_server(cls):
        cls.origin = BASE_ORIGIN_MOCK
        cls.host = BASE_HOST_MOCK

@dataclass
class HTTPRequest:
    url: str
    method: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, str]] = None
    
    def generate_headers(self, user_agent: str) -> Dict[str, str]:
        h = self.headers.copy()
        h["User-Agent"] = user_agent
        return h

def get_password_page_request() -> HTTPRequest:
    return HTTPRequest(
        url=BaseURL.origin + "/GetAccess/Login?Template=userpass_key&AUTHMETHOD=UserPassword",
        method="GET",
        headers={
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
        }
    )

def get_password_submit_request(html_inputs: List[HTMLInput]) -> HTTPRequest:
    body = {inp.name: inp.value for inp in html_inputs}
    return HTTPRequest(
        url=BaseURL.origin + "/GetAccess/Login",
        method="POST",
        headers={
            "Referer": BaseURL.origin + "/GetAccess/Login?Template=userpass_key&AUTHMETHOD=UserPassword",
            "Host": BaseURL.host,
            "Origin": BaseURL.origin,
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
        },
        body=body
    )

def get_otp_select_submit_request(html_inputs: List[HTMLInput], html_selects: List[HTMLSelect]) -> HTTPRequest:
    body = {inp.name: inp.value for inp in html_inputs}
    for sel in html_selects:
        if sel.selected_value is not None:
            body[sel.name] = sel.selected_value
    
    return HTTPRequest(
        url=BaseURL.origin + "/GetAccess/Login",
        method="POST",
        headers={
            "Referer": BaseURL.origin + "/GetAccess/Login?Template=idg_key&AUTHMETHOD=IG&GASF=CERTIFICATE,IG.GRID,IG.TOKENRO,IG.OTP&LOCALE=ja_JP&GAREASONCODE=13&GAIDENTIFICATIONID=UserPassword&GARESOURCEID=resourcelistID2&GAURI=https://portal.nap.gsic.titech.ac.jp/GetAccess/ResourceList&Reason=13&APPID=resourcelistID2&URI=https://portal.nap.gsic.titech.ac.jp/GetAccess/ResourceList",
            "Host": BaseURL.host,
            "Origin": BaseURL.origin,
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
        },
        body=body
    )

def get_matrix_code_submit_request(html_inputs: List[HTMLInput], html_selects: List[HTMLSelect]) -> HTTPRequest:
    body = {inp.name: inp.value for inp in html_inputs}
    for sel in html_selects:
        if sel.selected_value is not None:
             body[sel.name] = sel.selected_value

    return HTTPRequest(
        url=BaseURL.origin + "/GetAccess/Login",
        method="POST",
        headers={
            "Referer": BaseURL.origin + "/GetAccess/Login?Template=idg_key&AUTHMETHOD=IG&GASF=CERTIFICATE,IG.GRID,IG.TOKENRO,IG.OTP&LOCALE=ja_JP&GAREASONCODE=13&GAIDENTIFICATIONID=UserPassword&GARESOURCEID=resourcelistID2&GAURI=https://portal.nap.gsic.titech.ac.jp/GetAccess/ResourceList&Reason=13&APPID=resourcelistID2&URI=https://portal.nap.gsic.titech.ac.jp/GetAccess/ResourceList",
            "Host": BaseURL.host,
            "Origin": BaseURL.origin,
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
        },
        body=body
    )

def get_resource_list_page_request() -> HTTPRequest:
    return HTTPRequest(
        url=BaseURL.origin + "/GetAccess/ResourceList",
        method="GET",
        headers={
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
        }
    )
